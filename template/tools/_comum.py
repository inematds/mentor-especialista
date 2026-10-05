"""Funções compartilhadas pelos scripts do mentor (só biblioteca padrão)."""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import tempfile
import unicodedata
from datetime import date
from pathlib import Path

try:  # trava de arquivo (Linux/macOS); no Windows segue sem trava
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None

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
    """Caixa, acentos, pontuação, espaços e marcas de tempo [hh:mm:ss] fora — transcrição nunca é literal."""
    texto = re.sub(r"\[\d{1,2}:\d{2}(:\d{2})?\]", " ", texto)
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return " ".join(t.split())


def ler_manifesto(raiz: Path = RAIZ) -> list[dict]:
    p = raiz / "raw" / "MANIFESTO.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


@contextlib.contextmanager
def trava(raiz: Path = RAIZ):
    """Trava exclusiva do manifesto: coletores em paralelo (um subagente por fonte) não se atropelam."""
    (raiz / "raw").mkdir(parents=True, exist_ok=True)
    with open(raiz / "raw" / ".manifesto.lock", "w") as f:
        if fcntl:
            fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield
        finally:
            if fcntl:
                fcntl.flock(f, fcntl.LOCK_UN)


def _gravar_atomico(destino: Path, conteudo: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=destino.parent, prefix=".tmp-", suffix=destino.suffix)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(conteudo)
    os.replace(tmp, destino)


def registrar_item(tipo: str, url: str, arquivo: Path, titulo: str = "", raiz: Path = RAIZ) -> dict:
    """Acrescenta (ou atualiza pelo arquivo) um item no manifesto — com trava e escrita atômica."""
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
    with trava(raiz):
        itens = [i for i in ler_manifesto(raiz) if i.get("arquivo") != rel] + [item]
        _gravar_atomico(raiz / "raw" / "MANIFESTO.json", json.dumps(itens, ensure_ascii=False, indent=2) + "\n")
    return item


def registrar_falha(tipo: str, url: str, motivo: str, raiz: Path = RAIZ) -> None:
    p = raiz / "raw" / "RELATORIO-FALHAS.md"
    if not p.exists():
        p.write_text("# Relatório de falhas da coleta\n\n| data | tipo | origem | motivo |\n|---|---|---|---|\n", encoding="utf-8")
    with p.open("a", encoding="utf-8") as f:
        f.write(f"| {date.today().isoformat()} | {tipo} | {url} | {motivo.replace('|', '/')} |\n")


def ja_coletado(url: str, raiz: Path = RAIZ) -> bool:
    return any(i.get("url") == url for i in ler_manifesto(raiz))
