#!/usr/bin/env python3
"""Fase 4 — pronto? A resposta do mentor seguiu o loop (prova externa, não autoavaliação).

Checa:
  (a) a resposta tem todas as seções do perfil (mentor.config.json → "secoes_resposta" ou "secoes_revisao")
  (b) todo ID de regra citado (R1, R2…) existe em regras.md
  (c) com --transcript: houve ≥1 chamada Bash real, e a PREVISÃO foi escrita antes da primeira
      execução (texto com "previs…" antes do 1º Bash que roda algo — ler/listar não conta)

Uso: python3 tools/validar_resposta.py RESPOSTA.md [--perfil ensino|revisao] [--transcript ARQ.jsonl] [--raiz DIR]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import RAIZ, carregar_config, normalizar  # noqa: E402
from validar_citacoes import ler_regras  # noqa: E402

PADRAO = {
    "ensino": ["Pronto", "Previsão", "Saída real", "Versão quebrada", "Relatório"],
    "revisao": ["Previsão", "Reprodução", "Correção", "Lado a lado", "Relatório"],
}
CHAVE = {"ensino": "secoes_resposta", "revisao": "secoes_revisao"}
SO_LE = re.compile(r"^\s*(\S+=\S*\s+)*(cat|less|more|head|tail|ls|wc|grep|rg|sed\s+-n|find|stat|file|git\s+(status|log|diff|show)|echo|pwd|tree|mkdir|cd|touch|which|type)\b")


def eventos(transcript: Path) -> list[tuple[str, str]]:
    """[('T', texto) | ('B', comando)] do ASSISTENTE desta conversa, na ordem.

    Pedidos (do usuário ou de quem chamou o subagente) não contam como previsão, e eventos de
    subagentes que aparecem no stream da sessão principal (parent_tool_use_id) ficam de fora:
    cada subagente é avaliado pela própria transcrição.
    """
    out = []
    for linha in transcript.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            ev = json.loads(linha)
        except json.JSONDecodeError:
            continue
        msg = ev.get("message") or {}
        if ev.get("parent_tool_use_id") or (ev.get("type") or msg.get("role")) != "assistant":
            continue
        conteudo = msg.get("content")
        if not isinstance(conteudo, list):
            continue
        for c in conteudo:
            if not isinstance(c, dict):
                continue
            if c.get("type") == "text":
                out.append(("T", c.get("text", "")))
            elif c.get("type") == "tool_use" and c.get("name") == "Bash":
                out.append(("B", (c.get("input") or {}).get("command", "")))
    return out


def transcricoes(transcript: Path) -> list[Path]:
    """A transcrição dada + as dos subagentes da mesma sessão (Claude Code: <sessão>/subagents/*.jsonl)."""
    achadas = [transcript]
    sessao = transcript.stem
    for linha in transcript.read_text(encoding="utf-8", errors="ignore").splitlines()[:50]:
        try:
            sessao = json.loads(linha).get("session_id") or sessao
            if sessao != transcript.stem:
                break
        except json.JSONDecodeError:
            continue
    candidatos = [transcript.parent / sessao / "subagents"]
    candidatos += list((Path.home() / ".claude" / "projects").glob(f"*/{sessao}/subagents"))
    for pasta in candidatos:
        for sub in sorted(pasta.glob("*.jsonl")) if pasta.is_dir() else []:
            if sub not in achadas:
                achadas.append(sub)
    return achadas


def contar_bash(transcript: Path) -> int:
    return sum(1 for t in transcricoes(transcript) for k, _ in eventos(t) if k == "B")


VERSAO = re.compile(r"\s--?(version|help|V)\s*(2>\S+)?\s*$")  # consultar versão/ajuda não roda a lição
KIT = re.compile(r"^\s*(cd\s+\S+\s+)?python3?\s+(\S*/)?tools/(stats|validar_\w+|coletar_\w+)\.py\b")


def executa_algo(cmd: str) -> bool:
    """O comando roda código? Ler/listar e os scripts do próprio kit (tools/) não contam."""
    sem_aspas = re.sub(r"\"(\\.|[^\"\\])*\"|'[^']*'", "''", cmd)  # tira o conteúdo entre aspas: "a\|b" não é pipe
    segmentos = [seg for seg in re.split(r"&&|\|\||;|\||\n", sem_aspas) if seg.strip()]
    return not all(SO_LE.match(seg) or KIT.match(seg) or VERSAO.search(seg) for seg in segmentos)


def previu_antes(transcript: Path) -> bool | None:
    """Texto com 'previs' antes do 1º Bash que executa algo — avaliado em quem DEU a lição.

    Se a sessão chamou subagentes (o mentor roda como subagente), avalia cada subagente; a sessão
    principal só orquestra e confere depois. Sem subagentes, avalia a própria sessão.
    False se alguma transcrição avaliada rodou antes de prever; None se nenhuma executou nada.
    """
    todas = transcricoes(transcript)
    avaliar = todas[1:] or todas
    resultado = None
    for t in avaliar:
        viu = False
        for k, v in eventos(t):
            if k == "T" and re.search(r"previs", v, re.I):
                viu = True
            elif k == "B" and executa_algo(v):
                if not viu:
                    return False
                resultado = True
                break
    return resultado


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("resposta", type=Path)
    ap.add_argument("--transcript", type=Path)
    ap.add_argument("--perfil", choices=sorted(PADRAO), default="ensino")
    ap.add_argument("--raiz", type=Path, default=RAIZ)
    a = ap.parse_args(argv)
    raiz = a.raiz.resolve()
    secoes = carregar_config(raiz).get(CHAVE[a.perfil], PADRAO[a.perfil])
    texto = a.resposta.read_text(encoding="utf-8")
    titulos = {normalizar(m) for m in re.findall(r"^#{1,6}\s+(.+)$", texto, re.M)}
    erros = []

    for s in secoes:
        if not any(t.startswith(normalizar(s)) for t in titulos):
            erros.append(f"falta a seção '{s}'")

    ids_validos = {r["id"] for r in ler_regras((raiz / "regras.md").read_text(encoding="utf-8"))}
    citados = set(re.findall(r"\bR\d+\b", texto))
    if not citados:
        erros.append("nenhuma regra citada (o relatório deve dizer qual regra guiou cada passo)")
    for rid in sorted(citados - ids_validos):
        erros.append(f"regra citada não existe em regras.md: {rid}")

    if a.transcript:
        n = contar_bash(a.transcript)
        print(f"execuções Bash no transcript: {n}")
        if n == 0:
            erros.append("nenhuma execução real no transcript — 'Saída real' não foi produzida rodando")
        elif previu_antes(a.transcript) is False:
            erros.append("a primeira execução veio ANTES de qualquer previsão escrita — preveja, depois rode")

    print(f"seções exigidas: {len(secoes)}, regras citadas: {', '.join(sorted(citados)) or '-'}")
    if erros:
        print("REPROVADO:")
        for e in erros:
            print(f"  - {e}")
        return 1
    print("OK: resposta seguiu o loop")
    return 0


if __name__ == "__main__":
    sys.exit(main())
