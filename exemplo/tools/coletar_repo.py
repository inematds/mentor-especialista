#!/usr/bin/env python3
"""Coletor de repositórios git → raw/repos/<nome>.md

Junta README, docs e comentários de topo dos arquivos de código (onde o autor explica o porquê).
Uso: python3 tools/coletar_repo.py https://github.com/usuario/repo [...] [--max-arquivos 40]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import RAIZ, ja_coletado, registrar_falha, registrar_item, slugificar  # noqa: E402

DOCS = {".md", ".rst", ".txt"}
CODIGO = {".py", ".js", ".ts", ".go", ".rs", ".c", ".cpp", ".h", ".java", ".rb", ".sh"}


def cabecalho_comentado(texto: str, limite: int = 60) -> str:
    """Primeiro bloco de comentário/docstring do arquivo — onde mora a explicação."""
    linhas = texto.splitlines()[:limite]
    bloco, dentro = [], False
    for l in linhas:
        s = l.strip()
        if s.startswith(('"""', "'''")):
            bloco.append(s.strip("\"'"))
            if dentro or (s.count('"""') + s.count("'''")) >= 2:
                break
            dentro = True
        elif dentro or s.startswith(("#", "//", "/*", "*")):
            bloco.append(s.lstrip("#/* "))
        elif bloco:
            break
    return "\n".join(b for b in bloco if b).strip()


def coletar(url: str, raiz: Path, max_arquivos: int) -> bool:
    if ja_coletado(url, raiz):
        print(f"já coletado: {url}")
        return True
    nome = slugificar(url.rstrip("/").split("/")[-1].removesuffix(".git"))
    with tempfile.TemporaryDirectory() as t:
        r = subprocess.run(["git", "clone", "--depth", "1", "--quiet", url, t], capture_output=True, text=True, timeout=600)
        if r.returncode:
            registrar_falha("repo", url, r.stderr.strip()[:200], raiz)
            print(f"FALHA {url}")
            return False
        base = Path(t)
        partes = [f"# Repositório {nome}\n\nOrigem: {url}\n"]
        arquivos = sorted(p for p in base.rglob("*") if p.is_file() and ".git" not in p.parts)
        docs = [p for p in arquivos if p.suffix.lower() in DOCS][:max_arquivos]
        for p in docs:
            partes.append(f"\n\n## {p.relative_to(base)}\n\n{p.read_text(encoding='utf-8', errors='ignore')}")
        for p in [p for p in arquivos if p.suffix in CODIGO][:max_arquivos]:
            cab = cabecalho_comentado(p.read_text(encoding="utf-8", errors="ignore"))
            if len(cab.split()) >= 8:
                partes.append(f"\n\n## {p.relative_to(base)} (comentário de topo)\n\n{cab}")
    destino = raiz / "raw" / "repos" / f"{nome}.md"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("".join(partes) + "\n", encoding="utf-8")
    item = registrar_item("repo", url, destino, nome, raiz)
    print(f"ok {item['palavras']:>6} pal.  {destino.relative_to(raiz)}")
    return True


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", nargs="+")
    ap.add_argument("--raiz", type=Path, default=RAIZ)
    ap.add_argument("--max-arquivos", type=int, default=40)
    a = ap.parse_args(argv)
    ok = [coletar(u, a.raiz.resolve(), a.max_arquivos) for u in a.urls]
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
