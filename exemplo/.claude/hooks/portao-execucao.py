#!/usr/bin/env python3
"""Portão de execução: escreveu código e não rodou → o turno não termina.

Um script só, registrado em 3 eventos no .claude/settings.json do projeto:
  PostToolUse (Write|Edit|MultiEdit) → marca o arquivo de código como "sujo"
  PostToolUse (Bash)                 → limpa os sujos que o comando realmente executa
  Stop / SubagentStop                → bloqueia enquanto houver sujo

Estado por sessão em .mentor/estado/<session_id>.json (fora do git).
Não lê o transcript (o formato dele pode mudar entre versões).
Guarda anti-loop: com stop_hook_active=true sai 0 → no máximo 1 bloqueio por turno.
Qualquer erro interno → exit 0 (o portão nunca derruba a sessão).
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

PADRAO = {
    "extensoes_codigo": [".py", ".js", ".mjs", ".ts", ".tsx", ".sh", ".go", ".rs", ".rb", ".c", ".cpp", ".java"],
    "pastas_ignoradas": ["raw", "wiki", "docs", ".claude", ".mentor"],
    # comando de teste da linguagem → limpa todos os sujos daquela extensão
    "executores_teste": {
        ".py": ["pytest", "python3 -m pytest", "python -m pytest", "python3 -m unittest"],
        ".js": ["npm test", "node --test", "npx vitest", "npx jest"],
        ".ts": ["npm test", "npx vitest", "npx jest", "npx tsx"],
        ".go": ["go test", "go run"],
        ".rs": ["cargo test", "cargo run"],
    },
}
EDICAO = {"Write", "Edit", "MultiEdit"}


def raiz_projeto(evento: dict) -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or evento.get("cwd") or ".").resolve()


def config(raiz: Path) -> dict:
    cfg = dict(PADRAO)
    p = raiz / "mentor.config.json"
    if p.exists():
        cfg.update(json.loads(p.read_text(encoding="utf-8")).get("portao", {}))
    return cfg


def arq_estado(raiz: Path, sessao: str) -> Path:
    seguro = re.sub(r"[^A-Za-z0-9_.-]", "_", sessao or "sem-sessao")
    return raiz / ".mentor" / "estado" / f"{seguro}.json"


def ler(p: Path) -> list[str]:
    try:
        return json.loads(p.read_text(encoding="utf-8")).get("sujos", [])
    except (OSError, ValueError):
        return []


def gravar(p: Path, sujos: list[str]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"sujos": sorted(set(sujos))}), encoding="utf-8")


def eh_codigo(caminho: str, raiz: Path, cfg: dict) -> bool:
    p = Path(caminho)
    if p.suffix.lower() not in cfg["extensoes_codigo"]:
        return False
    try:
        rel = p.resolve().relative_to(raiz)
    except ValueError:
        return True  # fora do projeto, mas é código: conta
    return not (rel.parts and rel.parts[0] in cfg["pastas_ignoradas"])


def executa(cmd: str, sujo: str, cfg: dict) -> bool:
    p = Path(sujo)
    ext = p.suffix.lower()
    if any(t in cmd for t in cfg["executores_teste"].get(ext, [])):
        return True
    if ext == ".ts" and any(t in cmd for t in cfg["executores_teste"].get(".js", [])):
        return True
    # o comando cita o arquivo (python3 x.py, bash x.sh, node x.js, ./x.sh)…
    if re.search(rf"(^|[\s/'\"]){re.escape(p.name)}($|[\s'\";|&)])", cmd):
        return not re.match(r"^\s*(cat|less|head|tail|ls|wc|grep|rg|sed -n|git (add|diff|show|log))\b", cmd)
    # …ou roda como módulo (python3 -m pacote.modulo)
    return bool(re.search(rf"-m\s+[\w.]*\b{re.escape(p.stem)}\b", cmd))


def main() -> int:
    evento = json.load(sys.stdin)
    raiz = raiz_projeto(evento)
    cfg = config(raiz)
    estado = arq_estado(raiz, evento.get("session_id", ""))
    nome_evento = evento.get("hook_event_name", "")
    ferramenta = evento.get("tool_name", "")
    entrada = evento.get("tool_input") or {}

    if nome_evento == "PostToolUse" and ferramenta in EDICAO:
        caminho = entrada.get("file_path", "")
        if caminho and eh_codigo(caminho, raiz, cfg):
            gravar(estado, ler(estado) + [str(Path(caminho).resolve())])
        return 0

    if nome_evento == "PostToolUse" and ferramenta == "Bash":
        cmd = entrada.get("command", "")
        sujos = ler(estado)
        restantes = [s for s in sujos if not executa(cmd, s, cfg)]
        if restantes != sujos:
            gravar(estado, restantes)
        return 0

    if nome_evento in ("Stop", "SubagentStop"):
        if evento.get("stop_hook_active"):
            return 0
        sujos = ler(estado)
        if sujos:
            lista = ", ".join(Path(s).name for s in sujos)
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
