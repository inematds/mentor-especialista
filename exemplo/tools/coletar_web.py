#!/usr/bin/env python3
"""Coletor de páginas web (blog, artigos, docs) → raw/web/<slug>.md

Uso: python3 tools/coletar_web.py URL [URL...] [--tipo blog]
Sem dependências: baixa com urllib e extrai o texto do HTML.
Página com paywall/JS pesado → vai para raw/RELATORIO-FALHAS.md (colete à mão com coletar_arquivo.py).
"""
from __future__ import annotations

import argparse
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import RAIZ, ja_coletado, registrar_falha, registrar_item, slugificar  # noqa: E402

IGNORAR = {"script", "style", "nav", "footer", "header", "aside", "noscript", "svg", "form"}
BLOCO = {"p", "div", "section", "article", "li", "br", "tr", "pre", "blockquote"}


class Extrator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.partes: list[str] = []
        self.pulando = 0
        self.titulo = ""
        self._no_titulo = False

    def handle_starttag(self, tag, attrs):
        if tag in IGNORAR:
            self.pulando += 1
        elif tag == "title":
            self._no_titulo = True
        elif tag in {"h1", "h2", "h3", "h4"} and not self.pulando:
            self.partes.append("\n\n" + "#" * int(tag[1]) + " ")
        elif tag in BLOCO and not self.pulando:
            self.partes.append("\n\n" if tag != "li" else "\n- ")

    def handle_endtag(self, tag):
        if tag in IGNORAR and self.pulando:
            self.pulando -= 1
        elif tag == "title":
            self._no_titulo = False

    def handle_data(self, data):
        if self._no_titulo:
            self.titulo += data.strip()
        elif not self.pulando and data.strip():
            self.partes.append(" ".join(data.split()) + " ")

    def texto(self) -> str:
        linhas = [l.rstrip() for l in "".join(self.partes).splitlines()]
        out, vazio = [], False
        for l in linhas:
            if l.strip():
                out.append(l.strip())
                vazio = False
            elif not vazio:
                out.append("")
                vazio = True
        return "\n".join(out).strip() + "\n"


def coletar(url: str, tipo: str, raiz: Path, timeout: int) -> bool:
    if ja_coletado(url, raiz):
        print(f"já coletado: {url}")
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (mentor-especialista)"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            html = r.read().decode(r.headers.get_content_charset() or "utf-8", errors="ignore")
    except Exception as e:  # noqa: BLE001
        registrar_falha(tipo, url, f"download: {e}", raiz)
        print(f"FALHA {url}: {e}")
        return False
    ex = Extrator()
    ex.feed(html)
    corpo = ex.texto()
    if len(corpo.split()) < 80:
        registrar_falha(tipo, url, "texto curto demais (paywall/JS?) — colete à mão", raiz)
        print(f"FALHA {url}: texto curto demais")
        return False
    destino = raiz / "raw" / tipo / f"{slugificar(ex.titulo or url)}.md"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(f"# {ex.titulo or url}\n\nOrigem: {url}\n\n{corpo}", encoding="utf-8")
    item = registrar_item(tipo, url, destino, ex.titulo, raiz)
    print(f"ok {item['palavras']:>6} pal.  {destino.relative_to(raiz)}")
    return True


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", nargs="+")
    ap.add_argument("--tipo", default="web")
    ap.add_argument("--raiz", type=Path, default=RAIZ)
    ap.add_argument("--timeout", type=int, default=30)
    a = ap.parse_args(argv)
    ok = [coletar(u, a.tipo, a.raiz.resolve(), a.timeout) for u in a.urls]
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
