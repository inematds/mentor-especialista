#!/usr/bin/env python3
"""Cria o projeto de um mentor novo a partir do template.

Uso:
  python3 novo-mentor.py <slug> --nome "Nome do especialista" --dominio "o que ele ensina" [--destino DIR]

Exemplo:
  python3 novo-mentor.py prof-redes --nome "Profa. Redes" --dominio "ensinar redes neurais do zero" --destino ~/mentores

Gera <destino>/mentor-<slug>/ com raw/, wiki/, regras.md, tools/, o agente, 6 skills e o portão de execução.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent / "template"
TEXTO = {".md", ".py", ".json", ".txt", ".gitignore", ""}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Cria um mentor novo a partir do template.")
    ap.add_argument("slug", help="identificador curto: letras minúsculas, números e hífen (ex.: prof-redes)")
    ap.add_argument("--nome", required=True, help="nome do especialista")
    ap.add_argument("--dominio", required=True, help="o que o mentor ensina, numa frase estreita")
    ap.add_argument("--destino", type=Path, default=Path.cwd())
    ap.add_argument("--forcar", action="store_true", help="sobrescreve pasta existente")
    a = ap.parse_args(argv)

    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", a.slug):
        print("slug inválido: use letras minúsculas, números e hífen (ex.: prof-redes)", file=sys.stderr)
        return 2
    alvo = a.destino.expanduser().resolve() / f"mentor-{a.slug}"
    if alvo.exists() and not a.forcar:
        print(f"já existe: {alvo} (use --forcar para sobrescrever)", file=sys.stderr)
        return 1
    if alvo.exists():
        shutil.rmtree(alvo)

    trocas = {"{{SLUG}}": a.slug, "{{NOME}}": a.nome, "{{DOMINIO}}": a.dominio}
    for origem in sorted(TEMPLATE.rglob("*")):
        if "__pycache__" in origem.parts or origem.suffix == ".pyc":
            continue
        rel = str(origem.relative_to(TEMPLATE))
        for k, v in trocas.items():
            rel = rel.replace(k, a.slug if k == "{{SLUG}}" else v)
        destino = alvo / rel
        if origem.is_dir():
            destino.mkdir(parents=True, exist_ok=True)
            continue
        destino.parent.mkdir(parents=True, exist_ok=True)
        if origem.suffix in TEXTO or origem.name.startswith("."):
            conteudo = origem.read_text(encoding="utf-8")
            for k, v in trocas.items():
                conteudo = conteudo.replace(k, v)
            destino.write_text(conteudo, encoding="utf-8")
        else:
            shutil.copyfile(origem, destino)
        if origem.suffix == ".py":
            destino.chmod(0o755)

    for pasta in ("raw", "wiki/fontes", "wiki/temas", "wiki/principios", "wiki/metodos", "testes/respostas"):
        (alvo / pasta).mkdir(parents=True, exist_ok=True)
    print(f"Mentor criado em {alvo}\n")
    print("Próximos passos:")
    print(f"  1. cd {alvo}")
    print("  2. Preencha ESCOPO.md (fontes) e ajuste mentor.config.json (metas, transcritor)")
    print("  3. Abra o Claude Code nessa pasta e rode, em ordem:")
    for s in ("coletar", "compilar", "regras"):
        print(f"       /{a.slug}-{s}")
    print(f"  4. Use: /{a.slug}-ensina <dúvida>   /{a.slug}-revisa <arquivo>   /{a.slug}-ingere <link>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
