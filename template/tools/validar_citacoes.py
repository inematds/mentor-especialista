#!/usr/bin/env python3
"""Fase 3 — pronto? Toda citação de regras.md existe no raw/ e o status bate.

Formato esperado em regras.md (um bloco por regra):

    ## R1 — Construa para entender
    - status: ativa            # ativa | banco | inferencia
    - enunciado: Se não consegue construir, ainda não entendeu.
    - citacoes:
      - "trecho literal curto" — raw/blog/post.md#L12
      - "outro trecho" — raw/videos/abc.txt@00:12:30

Status:
  ativa      → ≥2 citações de ARQUIVOS diferentes
  banco      → ≥1 citação
  inferencia → 0 citações permitidas (o agente avisa que está inferindo)

A busca é feita em texto normalizado (caixa, acentos, pontuação, espaços).
Uso: python3 tools/validar_citacoes.py [--raiz DIR] [--regras ARQ]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import RAIZ, normalizar  # noqa: E402

CAB = re.compile(r"^##\s+(R\d+)\b(.*)$")
STATUS = re.compile(r"^\s*-\s*status:\s*(\w+)", re.I)
CIT = re.compile(r'^\s*-\s*["“](.+?)["”]\s*[—–-]+\s*(\S+)')


def ler_regras(texto: str) -> list[dict]:
    regras, atual = [], None
    for linha in texto.splitlines():
        if m := CAB.match(linha):
            atual = {"id": m.group(1), "titulo": m.group(2).strip(" —-"), "status": None, "citacoes": []}
            regras.append(atual)
        elif atual is None:
            continue
        elif m := STATUS.match(linha):
            atual["status"] = m.group(1).lower()
        elif m := CIT.match(linha):
            arquivo = re.split(r"[#@]", m.group(2), maxsplit=1)[0]
            atual["citacoes"].append({"trecho": m.group(1), "arquivo": arquivo, "local": m.group(2)})
    return regras


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", type=Path, default=RAIZ)
    ap.add_argument("--regras", type=Path)
    a = ap.parse_args(argv)
    raiz = a.raiz.resolve()
    arq_regras = a.regras or raiz / "regras.md"
    regras = ler_regras(arq_regras.read_text(encoding="utf-8"))
    cache: dict[str, str] = {}
    encontradas, faltando, erros = 0, 0, []

    if not regras:
        erros.append("nenhuma regra no formato '## R<n> — título'")
    for r in regras:
        if r["status"] not in ("ativa", "banco", "inferencia"):
            erros.append(f"{r['id']}: status inválido ou ausente ({r['status']})")
        for c in r["citacoes"]:
            p = raiz / c["arquivo"]
            if not str(c["arquivo"]).startswith("raw/") or not p.exists():
                faltando += 1
                erros.append(f"{r['id']}: arquivo de origem inexistente ou fora de raw/: {c['local']}")
                continue
            if c["arquivo"] not in cache:
                cache[c["arquivo"]] = normalizar(p.read_text(encoding="utf-8", errors="ignore"))
            if normalizar(c["trecho"]) in cache[c["arquivo"]]:
                encontradas += 1
            else:
                faltando += 1
                erros.append(f"{r['id']}: citação não encontrada em {c['arquivo']}: \"{c['trecho'][:60]}\"")
        arquivos = {c["arquivo"] for c in r["citacoes"]}
        if r["status"] == "ativa" and len(arquivos) < 2:
            erros.append(f"{r['id']}: 'ativa' exige ≥2 fontes diferentes (tem {len(arquivos)}) — mova para 'banco'")
        if r["status"] == "banco" and not arquivos:
            erros.append(f"{r['id']}: 'banco' exige ≥1 citação — ou marque 'inferencia'")

    ativas = sum(r["status"] == "ativa" for r in regras)
    print(f"{len(regras)} regras ({ativas} ativas), {encontradas} citações encontradas, {faltando} faltando")
    if erros:
        print("REPROVADO:")
        for e in erros:
            print(f"  - {e}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
