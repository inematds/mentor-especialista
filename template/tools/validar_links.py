#!/usr/bin/env python3
"""Fase 2 — pronto? A wiki está interligada e cobre o acervo.

Regras checadas:
  - todo [[link]] aponta para uma página existente em wiki/
  - toda página de wiki/fontes/ tem ≥1 link de saída
  - toda página de wiki/principios/ liga pelo menos uma página de fontes/
  - nº de páginas em wiki/fontes/ = nº de itens do manifesto
  - index.md, hot.md e log.md existem

Uso: python3 tools/validar_links.py [--raiz DIR]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import RAIZ, ler_manifesto  # noqa: E402

LINK = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", type=Path, default=RAIZ)
    a = ap.parse_args(argv)
    wiki = a.raiz.resolve() / "wiki"
    todas = sorted(wiki.rglob("*.md"))
    paginas = {p.stem: p for p in todas}
    fontes = {p.stem for p in (wiki / "fontes").glob("*.md")}
    erros: list[str] = []
    vistos: dict[str, Path] = {}
    for p in todas:
        if p.stem in vistos:
            erros.append(f"nome repetido (links ficam ambíguos): {vistos[p.stem].relative_to(wiki)} e {p.relative_to(wiki)}")
        vistos[p.stem] = p

    for nome in ("index", "hot", "log"):
        if nome not in paginas:
            erros.append(f"falta wiki/{nome}.md")

    total_links = 0
    for stem, p in paginas.items():
        alvos = [m.strip() for m in LINK.findall(p.read_text(encoding="utf-8"))]
        total_links += len(alvos)
        for alvo in alvos:
            if Path(alvo).name not in paginas:
                erros.append(f"link quebrado em {p.relative_to(wiki)}: [[{alvo}]]")
        if p.parent.name == "fontes" and not alvos:
            erros.append(f"fonte sem link de saída: {p.relative_to(wiki)}")
        if p.parent.name == "principios" and not any(Path(x).name in fontes for x in alvos):
            erros.append(f"princípio sem fonte: {p.relative_to(wiki)}")

    n_manifesto = len(ler_manifesto(a.raiz.resolve()))
    if len(fontes) != n_manifesto:
        erros.append(f"wiki/fontes tem {len(fontes)} páginas, manifesto tem {n_manifesto} itens")

    print(f"{len(paginas)} páginas, {total_links} links, {len(fontes)} fontes")
    if erros:
        print("REPROVADO:")
        for e in erros:
            print(f"  - {e}")
        return 1
    print("OK: 0 links quebrados")
    return 0


if __name__ == "__main__":
    sys.exit(main())
