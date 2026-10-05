#!/usr/bin/env python3
"""Fase 1 — pronto? Confere o acervo contra as metas de mentor.config.json.

Uso: python3 tools/stats.py [--raiz DIR]
Exit 0 = metas batidas; 1 = reprovado (motivos impressos).
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import RAIZ, carregar_config, ler_manifesto, sha256  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", type=Path, default=RAIZ)
    a = ap.parse_args(argv)
    raiz = a.raiz.resolve()
    itens = ler_manifesto(raiz)
    metas = carregar_config(raiz).get("metas_coleta", {})
    erros: list[str] = []

    if not itens:
        erros.append("manifesto vazio")
    por_tipo: dict[str, dict] = defaultdict(lambda: {"itens": 0, "palavras": 0})
    for i in itens:
        t = por_tipo[i.get("tipo", "?")]
        t["itens"] += 1
        t["palavras"] += int(i.get("palavras", 0))
        arq = raiz / i.get("arquivo", "")
        if not i.get("sha256"):
            erros.append(f"sem sha256: {i.get('arquivo')}")
        elif not arq.exists():
            erros.append(f"arquivo sumiu: {i.get('arquivo')}")
        elif sha256(arq) != i["sha256"]:
            erros.append(f"raw alterado depois da coleta (sha256 diferente): {i.get('arquivo')}")

    print(f"{'tipo':<12}{'itens':>7}{'palavras':>11}   meta")
    for tipo in sorted(set(por_tipo) | set(metas)):
        v, m = por_tipo.get(tipo, {"itens": 0, "palavras": 0}), metas.get(tipo, {})
        meta_txt = f"≥{m.get('itens', 0)} itens / ≥{m.get('palavras', 0)} pal." if m else "-"
        print(f"{tipo:<12}{v['itens']:>7}{v['palavras']:>11}   {meta_txt}")
        if m and (v["itens"] < m.get("itens", 0) or v["palavras"] < m.get("palavras", 0)):
            erros.append(f"meta não batida em '{tipo}'")
    total = sum(v["palavras"] for v in por_tipo.values())
    print(f"{'TOTAL':<12}{len(itens):>7}{total:>11}")

    if not (raiz / "raw" / "RELATORIO-FALHAS.md").exists():
        erros.append("raw/RELATORIO-FALHAS.md não existe (crie mesmo vazio: prova que as falhas foram olhadas)")

    if erros:
        print("\nREPROVADO:")
        for e in erros:
            print(f"  - {e}")
        return 1
    print("\nOK: acervo dentro das metas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
