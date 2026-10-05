#!/usr/bin/env python3
"""Portão de execução: escreveu código e não rodou → o turno não termina.

Um script só, registrado em 3 eventos no .claude/settings.json do projeto:
  PostToolUse (Write|Edit|MultiEdit) → marca o arquivo de código como "sujo"
  PostToolUse (Bash)                 → limpa os sujos que o comando realmente executa
  Stop / SubagentStop                → bloqueia enquanto houver sujo ainda não avisado

E um 2º portão, de PREVISÃO (kit 1.3):
  PreToolUse (Bash)                  → comando que executa código só passa se, no turno atual, o assistente
                                       já escreveu um texto com "Previsão" (o que espera ver). Ler/listar,
                                       scripts do kit (tools/) e --version/--help passam sempre.
  Motivo: no piloto, instruir "preveja antes de rodar" não mudou o comportamento em 3 rodadas — o modelo
  previa só no raciocínio. Instrução não basta; precisa de mecanismo.
  Se o comando vem de um subagente (agent_id), lê <sessão>/subagents/agent-<id>.jsonl; senão, transcript_path.
  Desligar: mentor.config.json → "portao": {"previsao": false}. Sem transcrição legível → deixa passar.

Estado por sessão em .mentor/estado/<session_id>.json (fora do git; estados com mais de 7 dias são apagados).
O portão de execução não lê o transcript; o de previsão lê (só os textos do assistente no turno).
Anti-loop: com stop_hook_active=true sai 0 e marca os sujos como "avisados" — o mesmo arquivo
só volta a bloquear se for editado de novo. No máximo 1 bloqueio por arquivo editado.
Qualquer erro interno → exit 0 (o portão nunca derruba a sessão).
"""
from __future__ import annotations

import json
import os
import re
import shlex
import sys
import time
from pathlib import Path

PADRAO = {
    "extensoes_codigo": [".py", ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".sh", ".go", ".rs", ".rb", ".c", ".cpp", ".java"],
    "pastas_ignoradas": ["raw", "wiki", "docs", ".claude", ".mentor"],
    # executor de testes da linguagem → limpa todos os sujos daquela extensão
    "executores_teste": {
        ".py": ["pytest", "python3 -m pytest", "python -m pytest", "python3 -m unittest", "python -m unittest"],
        ".js": ["npm test", "npm run test", "node --test", "npx vitest", "npx jest", "yarn test", "pnpm test"],
        ".ts": ["npm test", "npm run test", "npx vitest", "npx jest", "yarn test", "pnpm test"],
        ".go": ["go test"],
        ".rs": ["cargo test"],
    },
}
# extensões que usam os executores de outra
FAMILIA = {".mjs": ".js", ".cjs": ".js", ".jsx": ".js", ".tsx": ".ts"}
EDICAO = {"Write", "Edit", "MultiEdit"}
# portão de previsão: o que conta como EXECUTAR código (1ª palavra de um segmento)
INTERPRETADORES = {"python", "python3", "node", "bash", "sh", "zsh", "deno", "bun", "ruby", "perl", "php",
                   "go", "cargo", "java", "npx", "pytest", "uv", "poetry"}
KIT = re.compile(r"^(\S*/)?tools/(stats|validar_\w+|coletar_\w+)\.py\b")
VERSAO = re.compile(r"\s--?(version|help|V|h)\s*$")
# primeiro comando de um segmento que NÃO executa o arquivo citado
NAO_EXECUTA = {
    "cat", "less", "more", "head", "tail", "ls", "wc", "grep", "rg", "sed", "awk", "rm", "mv", "cp", "chmod",
    "chown", "touch", "echo", "printf", "tee", "diff", "stat", "file", "find", "du", "git", "ruff", "black",
    "flake8", "mypy", "pylint", "isort", "shellcheck", "prettier", "eslint", "vim", "vi", "nano", "code", "open",
    "pip", "pip3", "npm", "yarn", "pnpm", "apt", "brew", "mkdir", "ln", "readlink", "basename", "dirname",
}
SO_CHECA = re.compile(r"(-m\s+py_compile|-m\s+compileall|\b(ba|z)?sh\s+-n\b|\bnode\s+--check\b|\btsc\b.*--noEmit)")
SEPARADOR = re.compile(r"\s*(?:&&|\|\||;|\||\n)\s*")
ENV = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def config(raiz: Path) -> dict:
    cfg = json.loads(json.dumps(PADRAO))
    p = raiz / "mentor.config.json"
    if p.exists():
        cfg.update(json.loads(p.read_text(encoding="utf-8")).get("portao", {}))
    return cfg


def arq_estado(raiz: Path, sessao: str) -> Path:
    seguro = re.sub(r"[^A-Za-z0-9_.-]", "_", sessao or "sem-sessao")
    return raiz / ".mentor" / "estado" / f"{seguro}.json"


def ler(p: Path) -> dict:
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return {"sujos": d.get("sujos", []), "avisados": d.get("avisados", [])}
    except (OSError, ValueError):
        return {"sujos": [], "avisados": []}


def gravar(p: Path, estado: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({k: sorted(set(v)) for k, v in estado.items()}), encoding="utf-8")
    limite = time.time() - 7 * 86400
    for velho in p.parent.glob("*.json"):
        try:
            if velho.stat().st_mtime < limite:
                velho.unlink()
        except OSError:
            pass


def eh_codigo(caminho: Path, raiz: Path, cfg: dict) -> bool:
    if caminho.suffix.lower() not in cfg["extensoes_codigo"]:
        return False
    try:
        rel = caminho.relative_to(raiz)
    except ValueError:
        return True  # fora do projeto, mas é código: conta
    return not (rel.parts and rel.parts[0] in cfg["pastas_ignoradas"])


def tokens(segmento: str) -> list[str]:
    try:
        t = shlex.split(segmento)
    except ValueError:
        t = segmento.split()
    while t and ENV.match(t[0]):  # VAR=x python3 a.py
        t = t[1:]
    return t


def executa(cmd: str, sujo: str, base: Path, cfg: dict) -> bool:
    """O comando Bash executa (ou testa) este arquivo? Analisa segmento por segmento."""
    alvo = Path(sujo)
    ext = alvo.suffix.lower()
    executores = cfg["executores_teste"].get(FAMILIA.get(ext, ext), []) + cfg["executores_teste"].get(ext, [])
    atual = base
    for seg in SEPARADOR.split(cmd):
        t = tokens(seg)
        if not t:
            continue
        if t[0] == "cd" and len(t) > 1:
            atual = (atual / os.path.expanduser(t[1])).resolve()
            continue
        texto = " ".join(t)
        if any(re.match(rf"{re.escape(e)}(\s|$)", texto) for e in executores):
            return True
        if t[0] in NAO_EXECUTA or SO_CHECA.search(seg):
            continue
        for i, tok in enumerate(t):
            if tok.startswith("-") and tok != "-m":
                continue
            if i > 0 and t[i - 1] == "-m":  # python3 -m pacote.modulo
                partes = tok.split(".")
                candidatos = [atual.joinpath(*partes).with_suffix(ext), atual.joinpath(*partes, "__main__.py")]
                if any(c.resolve() == alvo for c in candidatos):
                    return True
                continue
            if (atual / os.path.expanduser(tok)).resolve() == alvo:
                return True
    return False


def _sem_aspas(cmd: str) -> str:
    return re.sub(r'"(\\.|[^"\\])*"|\'[^\']*\'', "''", cmd)


def executa_codigo(cmd: str) -> bool:
    """O comando roda código (interpretador, ./script, executor de testes)? Ler, listar, git e o kit não contam."""
    for seg in SEPARADOR.split(_sem_aspas(cmd)):
        t = tokens(seg)
        if not t or t[0] == "cd" or SO_CHECA.search(seg) or VERSAO.search(seg):
            continue
        prog = Path(t[0]).name
        if prog in ("python", "python3") and len(t) > 1 and KIT.match(t[1]):
            continue
        if prog in INTERPRETADORES or t[0].startswith("./") or (prog in ("npm", "yarn", "pnpm") and "test" in t[1:2]):
            return True
    return False


def transcricao_de(evento: dict) -> Path | None:
    tp = evento.get("transcript_path")
    if not tp:
        return None
    tp = Path(tp)
    if evento.get("agent_id"):
        sub = tp.parent / evento.get("session_id", tp.stem) / "subagents" / f"agent-{evento['agent_id']}.jsonl"
        return sub if sub.exists() else None
    return tp


def previu_no_turno(transcricao: Path) -> bool | None:
    """True se, desde a última mensagem humana, o assistente escreveu 'previs…'. None se não deu para ler."""
    try:
        linhas = transcricao.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return None
    viu = False
    for linha in linhas:
        try:
            ev = json.loads(linha)
        except ValueError:
            continue
        msg = ev.get("message") or {}
        papel = ev.get("type") or msg.get("role")
        conteudo = msg.get("content")
        if papel == "user":
            humano = isinstance(conteudo, str) or (isinstance(conteudo, list) and any(
                isinstance(c, dict) and c.get("type") == "text" for c in conteudo) and not any(
                isinstance(c, dict) and c.get("type") == "tool_result" for c in conteudo))
            if humano:
                viu = False
        elif papel == "assistant" and isinstance(conteudo, list):
            if any(isinstance(c, dict) and c.get("type") == "text" and re.search(r"previs", c.get("text", ""), re.I)
                   for c in conteudo):
                viu = True
    return viu


def main() -> int:
    evento = json.load(sys.stdin)
    raiz = Path(os.environ.get("CLAUDE_PROJECT_DIR") or evento.get("cwd") or ".").resolve()
    base = Path(evento.get("cwd") or raiz).resolve()
    cfg = config(raiz)
    p_estado = arq_estado(raiz, evento.get("session_id", ""))
    nome_evento = evento.get("hook_event_name", "")
    ferramenta = evento.get("tool_name", "")
    entrada = evento.get("tool_input") or {}

    if nome_evento == "PreToolUse" and ferramenta == "Bash":
        if not cfg.get("previsao", True) or not executa_codigo(entrada.get("command", "")):
            return 0
        tr = transcricao_de(evento)
        if tr is None or previu_no_turno(tr) is not False:
            return 0
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": ("Portão de previsão: antes de executar código, escreva na conversa uma linha "
                                         "'Previsão: …' com o que você espera ver (valor, saída ou erro). Depois rode "
                                         "e compare. Ler/listar arquivos não precisa de previsão."),
        }}))
        return 0

    if nome_evento == "PostToolUse" and ferramenta in EDICAO:
        caminho = entrada.get("file_path", "")
        if caminho:
            arq = (base / os.path.expanduser(caminho)).resolve()
            if eh_codigo(arq, raiz, cfg):
                e = ler(p_estado)
                e["sujos"].append(str(arq))
                e["avisados"] = [a for a in e["avisados"] if a != str(arq)]
                gravar(p_estado, e)
        return 0

    if nome_evento == "PostToolUse" and ferramenta == "Bash":
        e = ler(p_estado)
        restantes = [s for s in e["sujos"] if not executa(entrada.get("command", ""), s, base, cfg)]
        if restantes != e["sujos"]:
            e["sujos"] = restantes
            e["avisados"] = [a for a in e["avisados"] if a in restantes]
            gravar(p_estado, e)
        return 0

    if nome_evento in ("Stop", "SubagentStop"):
        e = ler(p_estado)
        if evento.get("stop_hook_active"):
            if e["sujos"]:
                e["avisados"] = e["sujos"]
                gravar(p_estado, e)
            return 0
        pendentes = [s for s in e["sujos"] if s not in e["avisados"]]
        if pendentes:
            lista = ", ".join(Path(s).name for s in pendentes)
            print(json.dumps({
                "decision": "block",
                "reason": (f"Você escreveu código e não rodou: {lista}. "
                           "Rode cada um (ou os testes) e mostre a saída real antes de dizer que funciona."),
            }))
        return 0
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 — o portão nunca derruba a sessão
        sys.exit(0)
