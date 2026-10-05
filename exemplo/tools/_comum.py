"""Funções compartilhadas pelos scripts do mentor (só biblioteca padrão)."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RAW = RAIZ / "raw"
WIKI = RAIZ / "wiki"
MANIFESTO = RAW / "MANIFESTO.json"
FALHAS = RAW / "RELATORIO-FALHAS.md"
CONFIG = RAIZ / "mentor.config.json"


def carregar_config(raiz: Path = RAIZ) -> dict:
    p = raiz / "mentor.config.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def sha256(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def contar_palavras(texto: str) -> int:
    return len(texto.split())


def slugificar(texto: str, limite: int = 60) -> str:
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t[:limite] or "item"


def normalizar(texto: str) -> str:
    """Caixa, acentos, pontuação e espaços fora — transcrição nunca é literal."""
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return " ".join(t.split())


def ler_manifesto(raiz: Path = RAIZ) -> list[dict]:
    p = raiz / "raw" / "MANIFESTO.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def registrar_item(tipo: str, url: str, arquivo: Path, titulo: str = "", raiz: Path = RAIZ) -> dict:
    """Acrescenta (ou atualiza pelo arquivo) um item no manifesto."""
    itens = ler_manifesto(raiz)
    rel = str(arquivo.resolve().relative_to(raiz.resolve()))
    item = {
        "id": slugificar(f"{tipo}-{Path(rel).stem}"),
        "tipo": tipo,
        "url": url,
        "titulo": titulo or Path(rel).stem,
        "arquivo": rel,
        "coletado_em": date.today().isoformat(),
        "palavras": contar_palavras(arquivo.read_text(encoding="utf-8", errors="ignore")),
        "sha256": sha256(arquivo),
    }
    itens = [i for i in itens if i.get("arquivo") != rel] + [item]
    (raiz / "raw").mkdir(exist_ok=True)
    (raiz / "raw" / "MANIFESTO.json").write_text(
        json.dumps(itens, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return item


def registrar_falha(tipo: str, url: str, motivo: str, raiz: Path = RAIZ) -> None:
    p = raiz / "raw" / "RELATORIO-FALHAS.md"
    if not p.exists():
        p.write_text("# Relatório de falhas da coleta\n\n| data | tipo | origem | motivo |\n|---|---|---|---|\n", encoding="utf-8")
    with p.open("a", encoding="utf-8") as f:
        f.write(f"| {date.today().isoformat()} | {tipo} | {url} | {motivo.replace('|', '/')} |\n")


def ja_coletado(url: str, raiz: Path = RAIZ) -> bool:
    return any(i.get("url") == url for i in ler_manifesto(raiz))
