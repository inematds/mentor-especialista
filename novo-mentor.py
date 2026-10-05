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
import json
from datetime import date
import re
import shutil
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent / "template"
TEXTO = {".md", ".py", ".json", ".txt", ".gitignore", ""}


def _trocar(texto: str, trocas: dict, escapar=lambda v: v) -> str:
    for k, v in trocas.items():
        texto = texto.replace(k, escapar(v))
    return texto


def preencher(conteudo: str, sufixo: str, trocas: dict) -> str:
    """Substitui os placeholders escapando conforme o contexto (JSON, frontmatter YAML entre aspas)."""
    if sufixo == ".json":
        return _trocar(conteudo, trocas, lambda v: json.dumps(v, ensure_ascii=False)[1:-1])
    if sufixo == ".md" and conteudo.startswith("---\n") and "\n---\n" in conteudo[4:]:
        fim = conteudo.index("\n---\n", 4) + 5
        yaml_escape = lambda v: v.replace("\\", "\\\\").replace('"', '\\"')  # noqa: E731
        return _trocar(conteudo[:fim], trocas, yaml_escape) + _trocar(conteudo[fim:], trocas)
    return _trocar(conteudo, trocas)


# o que --atualizar substitui (código e instruções do kit); acervo, wiki, regras, escopo e respostas ficam
ATUALIZAVEL = ("tools/", ".claude/", "testes/aceitacao/README.md", "testes/aceitacao/script_emoji.py",
               "testes/aceitacao/comentarios.json", ".gitignore")


def gerar(alvo: Path, trocas: dict, slug: str, so=None, backup: Path | None = None) -> list[str]:
    """Copia o template para alvo. Com `so`, copia só os caminhos que começam por um desses prefixos."""
    escritos = []
    for origem in sorted(TEMPLATE.rglob("*")):
        if "__pycache__" in origem.parts or origem.suffix == ".pyc" or origem.is_dir():
            continue
        rel = str(origem.relative_to(TEMPLATE)).replace("{{SLUG}}", slug)
        if so is not None and not rel.startswith(so):
            continue
        destino = alvo / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        if origem.suffix in TEXTO or origem.name.startswith("."):
            novo = preencher(origem.read_text(encoding="utf-8"), origem.suffix, trocas)
            if destino.exists() and destino.read_text(encoding="utf-8", errors="ignore") == novo:
                continue
            if backup and destino.exists():
                (backup / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(destino, backup / rel)
            destino.write_text(novo, encoding="utf-8")
        else:
            shutil.copyfile(origem, destino)
        if origem.suffix == ".py":
            destino.chmod(0o755)
        escritos.append(rel)
    return escritos


def atualizar(pasta: Path) -> int:
    """Leva um mentor existente para a versão atual do kit sem tocar no conteúdo dele."""
    pasta = pasta.expanduser().resolve()
    cfg_p = pasta / "mentor.config.json"
    if not cfg_p.exists():
        print(f"não é um mentor (falta mentor.config.json): {pasta}", file=sys.stderr)
        return 1
    cfg = json.loads(cfg_p.read_text(encoding="utf-8"))
    slug = cfg.get("slug", "")
    trocas = {"{{SLUG}}": slug, "{{NOME}}": cfg.get("especialista", ""), "{{DOMINIO}}": cfg.get("dominio", "")}
    backup = pasta / ".mentor" / f"backup-{date.today().isoformat()}"
    escritos = gerar(pasta, trocas, slug, so=ATUALIZAVEL, backup=backup)
    # config: só acrescenta chaves novas do template, nunca sobrescreve as do usuário
    modelo = json.loads(preencher((TEMPLATE / "mentor.config.json").read_text(encoding="utf-8"), ".json", trocas))
    novas = [k for k in modelo if k not in cfg]
    for k in novas:
        cfg[k] = modelo[k]
    if novas:
        cfg_p.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    versao = (TEMPLATE.parent / "VERSION").read_text().strip() if (TEMPLATE.parent / "VERSION").exists() else "?"
    print(f"Mentor {slug} atualizado para o kit {versao}: {len(escritos)} arquivo(s)"
          + (f", config +{', '.join(novas)}" if novas else ""))
    for rel in escritos:
        print(f"  {rel}")
    if backup.exists():
        print(f"Versões anteriores em {backup.relative_to(pasta)} (se você tinha personalizado o agente, compare).")
    print("Não mexi em: raw/, wiki/, regras.md, ESCOPO.md, CLAUDE.md, testes/respostas/.")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Cria um mentor novo a partir do template, ou atualiza um existente.")
    ap.add_argument("slug", nargs="?", help="identificador curto: letras minúsculas, números e hífen (ex.: prof-redes)")
    ap.add_argument("--nome", help="nome do especialista")
    ap.add_argument("--dominio", help="o que o mentor ensina, numa frase estreita")
    ap.add_argument("--destino", type=Path, default=Path.cwd())
    ap.add_argument("--forcar", action="store_true", help="sobrescreve pasta existente")
    ap.add_argument("--atualizar", type=Path, metavar="PASTA", help="atualiza um mentor já criado para esta versão do kit")
    a = ap.parse_args(argv)

    if a.atualizar:
        return atualizar(a.atualizar)
    if not (a.slug and a.nome and a.dominio):
        ap.error("informe <slug> --nome --dominio (ou --atualizar PASTA)")
    if any(c in v for v in (a.nome, a.dominio) for c in "\n\r"):
        print("--nome e --dominio devem ter uma linha só", file=sys.stderr)
        return 2
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", a.slug):
        print("slug inválido: use letras minúsculas, números e hífen (ex.: prof-redes)", file=sys.stderr)
        return 2
    alvo = a.destino.expanduser().resolve() / f"mentor-{a.slug}"
    if alvo.exists() and not a.forcar:
        print(f"já existe: {alvo} (use --forcar para sobrescrever, ou --atualizar para só atualizar o kit)", file=sys.stderr)
        return 1
    if alvo.exists():
        shutil.rmtree(alvo)

    trocas = {"{{SLUG}}": a.slug, "{{NOME}}": a.nome, "{{DOMINIO}}": a.dominio}
    gerar(alvo, trocas, a.slug)
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
