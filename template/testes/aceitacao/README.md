# Testes de aceitação do mentor

Três tarefas congeladas. Rode cada uma numa sessão nova do Claude Code, dentro deste projeto, e registre o resultado em `RESULTADOS.md`.

## 1. Construir e ensinar

```
/{{SLUG}}-ensina <algo pequeno e real do domínio que você ainda não domina>
```

Exemplo para programação: "me ensina a fazer um tokenizador BPE do zero".

**Passa se** `python3 tools/validar_resposta.py testes/respostas/<arquivo>.md` → exit 0 **e** você entendeu algo que não sabia.

## 2. Revisar um script "que funciona"

Use o `script_emoji.py` desta pasta. Ele roda no terminal comum e quebra num terminal sem UTF-8.

```
/{{SLUG}}-revisa testes/aceitacao/script_emoji.py
```

**Passa se** o mentor **previu** a quebra antes de rodar, **reproduziu** com `PYTHONIOENCODING=cp1252` (→ `UnicodeEncodeError`), corrigiu e rodou original e corrigido lado a lado.

## 3. Ingerir uma fonte nova

```
/{{SLUG}}-ingere <link novo do especialista>
```

**Passa se** `wiki/log.md` ganhou uma linha, apareceu a página nova em `wiki/fontes/`, os três validadores dão exit 0 e (se houver) uma regra `banco` foi promovida.
