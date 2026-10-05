---
name: exemplo-compilar
description: "Fase 2 — compila raw/ numa wiki interligada (fontes, temas, princípios, métodos, index, hot, log) sem tocar no raw. Use com '/exemplo-compilar' ou 'montar a wiki'."
---

# Compilar a wiki

O `raw/` é **somente leitura**. A wiki é o que o mentor consulta.

## Páginas

| Pasta | Uma página por… | Conteúdo mínimo |
|---|---|---|
| `wiki/fontes/` | item do `raw/MANIFESTO.json` (nome = `id` do item) | resumo em 5–10 linhas, ideias centrais, `Arquivo: raw/...`, links para temas/princípios/métodos |
| `wiki/temas/` | assunto que a pessoa domina | o que ela sabe sobre isso + `[[fontes]]` |
| `wiki/principios/` | coisa que ela defende repetidamente | enunciado + trechos curtos + **≥1 `[[fonte]]`** |
| `wiki/metodos/` | jeito de fazer: como explica, depura, constrói, revisa | passos + exemplos + `[[fontes]]` |

Arquivos de controle:
- `wiki/index.md`: mapa de todas as páginas por pasta.
- `wiki/hot.md`: 10–20 conceitos mais citados, com 1 linha cada (é a porta de entrada do mentor).
- `wiki/log.md`: o que entrou, quando, o que mudou (só acrescentar).

## Como fazer

1. Trabalhe em lotes de fontes. Para acervo grande, use subagentes por lote. Cada um devolve as páginas de fonte e uma lista de temas, princípios e métodos candidatos.
2. Junte os candidatos: mesmo conceito = mesma página. Links `[[nome-da-pagina]]` nos dois sentidos.
3. Rode e mostre a saída:
   ```
   python3 tools/validar_links.py
   ```
   Pronto = exit 0 (0 links quebrados, toda fonte com link, todo princípio com fonte, nº de fontes = nº do manifesto).
