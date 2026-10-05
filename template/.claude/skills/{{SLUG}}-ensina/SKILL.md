---
name: {{SLUG}}-ensina
description: "Ensina algo construindo junto, no método de {{NOME}} — chama o subagente {{SLUG}}-mentor e confere a resposta regra por regra. Use com '/{{SLUG}}-ensina <dúvida>' ou 'me ensina X construindo'."
---

# Ensinar

1. Passe a dúvida do usuário ao subagente **{{SLUG}}-mentor**, sem reescrevê-la. Se o pedido estiver vago, o mentor pergunta antes.
2. Quando o mentor responder, salve a resposta em `testes/respostas/<data>-<slug-da-duvida>.md`.
3. Confira por fora (não aceite autoavaliação):
   ```
   python3 tools/validar_resposta.py testes/respostas/<arquivo>.md --transcript <log .jsonl da sessão, se tiver>
   ```
4. Mostre ao usuário a resposta do mentor + um checklist de **1 linha por regra ativa**:
   `R1 ✓ — construiu a menor versão (seção Menor versão)` / `R3 ✗ — não previu antes de rodar`.
   Cada ✓ aponta o trecho da resposta que o comprova. Se houver ✗, devolva ao mentor para corrigir **uma vez**.
