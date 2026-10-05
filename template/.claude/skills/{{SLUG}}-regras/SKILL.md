---
name: {{SLUG}}-regras
description: Fase 3 — extrai da wiki as regras de conduta de {{NOME}}, cada uma com citação + localizador, e valida contra o raw. Use com "/{{SLUG}}-regras" ou "extrair as regras".
---

# Extrair as regras

Regra = **o que a pessoa FAZ** de forma recorrente ao ensinar/construir, não uma frase de efeito.
Mire em 5–9 regras. Menos regras e mais fortes é melhor que muitas e fracas.

1. Leia `wiki/principios/` e `wiki/metodos/`. Liste os comportamentos que aparecem em várias fontes.
2. Para cada regra, escreva em `regras.md` **exatamente** neste formato:
   ```
   ## R1 — Título curto
   - status: ativa
   - enunciado: uma frase de ação.
   - citacoes:
     - "trecho curto, copiado do raw" — raw/videos/x.txt@00:12:30
     - "outro trecho" — raw/blog/y.md
   - no mentor: como isso aparece na resposta (ex.: seção Previsão)
   ```
3. Status:
   - `ativa`: ≥2 citações de arquivos **diferentes**.
   - `banco`: só 1 fonte por enquanto (espera a 2ª).
   - `inferencia`: sem citação. O mentor avisa ao usar.
4. **Copie o trecho do raw. Não parafraseie.** Trechos curtos, de 5 a 25 palavras.
5. Rode e mostre a saída:
   ```
   python3 tools/validar_citacoes.py
   ```
   Pronto = exit 0. Uma citação não encontrada se corrige copiando do raw de novo, nunca relaxando o validador.
