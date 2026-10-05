"""Resume comentários de um arquivo JSON e grava um relatório.

Funciona no terminal do autor. Seu mentor deve descobrir onde quebra.
"""
import json
import sys
from pathlib import Path

ENTRADA = Path(__file__).with_name("comentarios.json")
SAIDA = Path(__file__).with_name("relatorio.txt")


def carregar():
    return json.loads(ENTRADA.read_text(encoding="utf-8"))


def perguntas(comentarios):
    resultado = []
    for c in comentarios:
        texto = c["texto"].strip()
        if texto.endswith("?"):
            resultado.append(texto)
    return resultado


def main():
    comentarios = carregar()
    print(f"🔎 lendo {len(comentarios)} comentários…")
    achadas = perguntas(comentarios)
    for p in achadas:
        print("❓", p)
    SAIDA.write_text("\n".join(achadas), encoding="utf-8")
    print(f"✅ {len(achadas)} perguntas salvas em {SAIDA.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
