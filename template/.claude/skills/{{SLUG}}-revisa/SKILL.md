---
name: {{SLUG}}-revisa
description: "Revisão antes de entregar, no método de {{NOME}} — prevê onde quebra, reproduz, corta o que sobra e prova que a versão enxuta faz o mesmo. Use com '/{{SLUG}}-revisa <arquivo>' ou 'revisa antes de eu entregar'."
---

# Revisar

Passe o arquivo ao subagente **{{SLUG}}-mentor** pedindo a revisão no formato de revisão dele:
**Previsão → Reprodução → Correção → Lado a lado → Relatório**.

1. **Previsão primeiro, sem rodar nada:** quem recebe aceitaria isto? O que cortaria? Onde quebra
   (codificação do terminal, sistema operacional, caminho, dados reais, rede)?
2. **Reproduza** a falha prevista e mostre a saída real (ex.: codificação: `PYTHONIOENCODING=cp1252 python3 script.py`).
3. **Corrija e enxugue** em `<nome>.revisado.<ext>` ao lado do original (o original não muda).
4. **Lado a lado:** rode os dois com a mesma entrada e prove que a saída útil é a mesma.
5. Salve a revisão em `testes/respostas/<data>-revisao-<nome>.md` e confira por fora:
   ```
   python3 tools/validar_resposta.py testes/respostas/<arquivo>.md --perfil revisao
   ```
Temporários em `.mentor/tmp/`.
