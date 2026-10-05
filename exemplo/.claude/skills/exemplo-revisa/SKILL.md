---
name: exemplo-revisa
description: Revisão antes de entregar, no método de Profa. Lia (personagem fictícia) — prevê onde quebra, reproduz, corta o que sobra e prova que a versão enxuta faz o mesmo. Use com "/exemplo-revisa <arquivo>" ou "revisa antes de eu entregar".
---

# Revisar

Passe o arquivo ao subagente **exemplo-mentor** com este pedido:

1. **Quem recebe aceitaria isto? O que cortaria?** Liste o que não se justifica.
2. **Onde quebra?** Preveja pelo menos 1 falha de ambiente: codificação do terminal, sistema operacional, caminho, dados reais, rede.
3. **Reproduza** a falha prevista e mostre a saída real. Exemplo para codificação: `PYTHONIOENCODING=cp1252 python3 script.py`.
4. **Corrija e enxugue.** Rode a versão original e a nova **lado a lado** com a mesma entrada, e mostre que a saída útil é a mesma.
5. Feche com o Relatório: o que rodou, o que saiu, o que mudou e a regra de cada passo.

Não altere o arquivo original. A versão nova vai ao lado, com sufixo `.revisado`, até o usuário aprovar.
