#!/usr/bin/env python3
"""Fase 4 — pronto? A resposta do mentor seguiu o loop (prova externa, não autoavaliação).

Checa:
  (a) a resposta tem todas as seções de mentor.config.json → "secoes_resposta"
  (b) todo ID de regra citado (R1, R2…) existe em regras.md
  (c) com --transcript: houve ≥1 chamada Bash real no transcript (.jsonl do Claude Code)

Uso: python3 tools/validar_resposta.py RESPOSTA.md [--transcript ARQ.jsonl] [--raiz DIR]
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

PADRAO = ["Pronto", "Previsão", "Saída real", "Versão quebrada", "Relatório"]


def contar_bash(transcript: Path) -> int:
    n = 0
    for linha in transcript.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            ev = json.loads(linha)
        except json.JSONDecodeError:
            continue
        conteudo = (ev.get("message") or {}).get("content")
        if isinstance(conteudo, list):
            n += sum(1 for c in conteudo if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") == "Bash")
    return n


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("resposta", type=Path)
    ap.add_argument("--transcript", type=Path)
    ap.add_argument("--raiz", type=Path, default=RAIZ)
    a = ap.parse_args(argv)
    raiz = a.raiz.resolve()
    secoes = carregar_config(raiz).get("secoes_resposta", PADRAO)
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
