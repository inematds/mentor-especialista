#!/usr/bin/env python3
"""Coletor de vídeos → raw/videos/<slug>.txt (texto com marcas de tempo [hh:mm:ss]).

Ordem:
  1. legenda que já existe (yt-dlp --skip-download, sem baixar o vídeo)
  2. se não houver e mentor.config.json tiver "transcrever_cmd": roda o SEU transcritor
     (Whisper local, faster-whisper, o pipeline da sua casa…). Placeholders: {url} {saida}
     O comando deve gravar um .txt / .srt / .vtt dentro de {saida}.
  3. senão → raw/RELATORIO-FALHAS.md

Uso: python3 tools/coletar_video.py URL [URL...] [--idiomas pt,en]
"""
from __future__ import annotations

import argparse
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import RAIZ, carregar_config, ja_coletado, registrar_falha, registrar_item, slugificar  # noqa: E402

TEMPO = re.compile(r"(\d{1,2}:)?(\d{2}):(\d{2})[.,]\d{3}\s*-->")


def legenda_para_texto(conteudo: str) -> str:
    """VTT/SRT → linhas '[hh:mm:ss] texto', sem as repetições típicas de legenda automática."""
    saida, ultima, marca = [], "", "00:00:00"
    for linha in conteudo.splitlines():
        if m := TEMPO.search(linha):
            h = (m.group(1) or "00:").rstrip(":")
            marca = f"{int(h):02d}:{m.group(2)}:{m.group(3)}"
            continue
        limpa = re.sub(r"<[^>]+>", "", linha).strip()
        if not limpa or limpa.isdigit() or limpa.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
            continue
        if limpa != ultima:
            saida.append(f"[{marca}] {limpa}")
            ultima = limpa
    return "\n".join(saida) + "\n"


def tentar_legenda(url: str, idiomas: str, tmp: Path, timeout: int) -> tuple[str, str]:
    if not shutil.which("yt-dlp"):
        return "", "yt-dlp não instalado"
    cmd = ["yt-dlp", "--skip-download", "--write-subs", "--write-auto-subs", "--sub-langs", idiomas,
           "--sub-format", "vtt/srt/best", "-o", str(tmp / "%(title)s.%(ext)s"), url]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return "", "timeout na legenda"
    arquivos = sorted(tmp.glob("*.vtt")) + sorted(tmp.glob("*.srt"))
    if not arquivos:
        return "", "sem legenda"
    titulo = arquivos[0].name.split(".")[0]
    return legenda_para_texto(arquivos[0].read_text(encoding="utf-8", errors="ignore")), titulo


def tentar_transcritor(url: str, cmd_tpl: str, tmp: Path, timeout: int) -> tuple[str, str]:
    cmd = cmd_tpl.format(url=shlex.quote(url), saida=shlex.quote(str(tmp)))
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return "", "timeout no transcritor"
    for ext in ("*.vtt", "*.srt"):
        if achados := sorted(tmp.rglob(ext)):
            return legenda_para_texto(achados[0].read_text(encoding="utf-8", errors="ignore")), achados[0].stem
    if achados := sorted(tmp.rglob("*.txt")):
        return achados[0].read_text(encoding="utf-8", errors="ignore"), achados[0].stem
    return "", f"transcritor não gerou texto (exit {r.returncode})"


def coletar(url: str, idiomas: str, raiz: Path, cfg: dict) -> bool:
    if ja_coletado(url, raiz):
        print(f"já coletado: {url}")
        return True
    timeout = int(cfg.get("timeout_video_s", 3600))
    with tempfile.TemporaryDirectory() as t:
        texto, info = tentar_legenda(url, idiomas, Path(t), 300)
        origem = "legenda"
        if not texto and cfg.get("transcrever_cmd"):
            texto, info = tentar_transcritor(url, cfg["transcrever_cmd"], Path(t), timeout)
            origem = "transcrição local"
    if not texto.strip():
        registrar_falha("video", url, info, raiz)
        print(f"FALHA {url}: {info}")
        return False
    destino = raiz / "raw" / "videos" / f"{slugificar(info)}.txt"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(f"# {info}\nOrigem: {url}\nTexto: {origem}\n\n{texto}", encoding="utf-8")
    item = registrar_item("video", url, destino, info, raiz)
    print(f"ok {item['palavras']:>6} pal.  {destino.relative_to(raiz)}  ({origem})")
    return True


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", nargs="+")
    ap.add_argument("--idiomas", default=None, help="ex.: pt,en (padrão: mentor.config.json)")
    ap.add_argument("--raiz", type=Path, default=RAIZ)
    a = ap.parse_args(argv)
    raiz = a.raiz.resolve()
    cfg = carregar_config(raiz)
    idiomas = a.idiomas or ",".join(cfg.get("idiomas_legenda", ["pt", "en"]))
    ok = [coletar(u, idiomas, raiz, cfg) for u in a.urls]
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
