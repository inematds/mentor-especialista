#!/usr/bin/env python3
"""Coletor de arquivos locais → raw/<tipo>/

Para o que não dá (ou não vale pagar) para baixar automaticamente:
exportação de posts de redes sociais, notas, PDFs já convertidos em texto, transcrições feitas fora.

Uso: python3 tools/coletar_arquivo.py ARQ [ARQ...] --tipo posts [--origem "export de 2026-10"]
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import RAIZ, registrar_falha, registrar_item, slugificar  # noqa: E402

TEXTO = {".md", ".txt", ".srt", ".vtt", ".json", ".csv", ".html"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivos", nargs="+", type=Path)
    ap.add_argument("--tipo", required=True, help="posts, notas, palestras, livro…")
    ap.add_argument("--origem", default="", help="de onde veio (vai para o campo url do manifesto)")
    ap.add_argument("--raiz", type=Path, default=RAIZ)
    a = ap.parse_args(argv)
    raiz, falhou = a.raiz.resolve(), False
    for arq in a.arquivos:
        if not arq.is_file() or arq.suffix.lower() not in TEXTO:
            registrar_falha(a.tipo, str(arq), "não é arquivo de texto (converta para .txt/.md antes)", raiz)
            print(f"FALHA {arq}")
            falhou = True
            continue
        destino = raiz / "raw" / a.tipo / f"{slugificar(arq.stem)}{arq.suffix.lower()}"
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(arq, destino)
        item = registrar_item(a.tipo, a.origem or f"arquivo:{arq.name}", destino, arq.stem, raiz)
        print(f"ok {item['palavras']:>6} pal.  {destino.relative_to(raiz)}")
    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main())
