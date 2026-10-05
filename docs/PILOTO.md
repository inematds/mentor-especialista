# Procedimento do piloto — o primeiro mentor real

Roteiro para levar **um especialista de verdade** por todas as fases, numa sessão do Claude Code, e saber no fim, com evidência, se o kit funciona. Leva cerca de 1 dia de trabalho (mais o tempo de máquina, se houver transcrição).

> Regra do piloto: **não conserte o kit durante o piloto.** Anote cada problema em `PILOTO-DIARIO.md` (tabela no fim) e siga em frente se der. As correções entram depois, numa versão nova do kit.

---

## 0. Antes de começar (15 min)

**Escolha o especialista.** Bons candidatos:
- tem **muito material público em texto ou com legenda** (vídeos legendados, blog, repositórios);
- ensina de um jeito **reconhecível** (você consegue dizer "ele sempre faz X");
- é de um domínio **que você conhece o bastante para julgar** se o mentor acertou.

Uma opção forte é **você mesmo**: suas aulas e lives como acervo. Não há questão de direitos, e o mentor vira a voz didática da sua marca.

**Defina o domínio numa frase estreita.** Exemplo: "ensinar automação com Claude Code para iniciantes", e não "tudo sobre IA".

**Separe as fontes do piloto:** 20–50 itens no total, misturando tipos.
- 10–20 vídeos (de preferência com legenda)
- 5–15 textos (blog, newsletter, docs)
- 1–3 repositórios
- 1 exportação manual (posts), se houver

**Verifique o ambiente:**
```bash
python3 --version   # 3.10+
git --version
claude --version
yt-dlp --version    # opcional, para legendas
```

---

## 1. Criar o mentor (5 min)

```bash
cd ~/caminho/do/kit/mentor-especialista
git pull
python3 novo-mentor.py <slug> --nome "<Nome>" --dominio "<domínio em uma frase>" --destino ~/mentores
cd ~/mentores/mentor-<slug>
git init -q && git add -A && git commit -qm "mentor <slug>: projeto gerado"   # para ver o que cada fase muda
```

**Confira:** a pasta tem `.claude/agents/<slug>-mentor.md`, 6 pastas em `.claude/skills/` e `.claude/settings.json` com os hooks.

---

## 2. Escopo e configuração (20 min)

1. Preencha o `ESCOPO.md`: uma linha por fonte (tipo, URL, coletor).
2. No `mentor.config.json`:
   - `metas_coleta`: metas que você **sabe** que dá para bater (ex.: `video` 10 itens / 30000 palavras; `blog` 5 / 8000).
   - `idiomas_legenda`: ex. `["pt", "en"]`.
   - `transcrever_cmd`: o seu transcritor local, com teto de memória (exemplos em `docs/ADAPTAR.md`). Sem transcritor, os vídeos sem legenda vão para o relatório de falhas, e tudo bem para o piloto.
3. Commit: `git commit -am "escopo"`.

---

## 3. Fase 1 — Coleta (30 min + máquina)

Abra o Claude Code **dentro da pasta do mentor** (`claude`) e rode:

```
/<slug>-coletar
```

**Passa se:**
```bash
python3 tools/stats.py      # exit 0
```

**Observe e anote:**
- [ ] Usou um subagente por fonte (em paralelo)?
- [ ] Algum coletor falhou? Por quê? (veja `raw/RELATORIO-FALHAS.md`)
- [ ] Quanto tempo levou? Quantas palavras no total?
- [ ] Alguma tentativa de usar API paga? (não deveria)

Commit: `git add -A && git commit -qm "fase 1: acervo"`.

---

## 4. Fase 2 — Wiki (1–2 h)

```
/<slug>-compilar
```

**Passa se:**
```bash
python3 tools/validar_links.py   # exit 0
```

**Observe e anote:**
- [ ] O `wiki/hot.md` reflete mesmo o que a pessoa mais fala? (seu julgamento)
- [ ] Os princípios são **dela** ou genéricos de IA? Marque 3 páginas como boas e 3 como ruins.
- [ ] O `raw/` ficou intocado? (`git status raw/` deve vir vazio)

Commit.

---

## 5. Fase 3 — Regras (30–60 min)

```
/<slug>-regras
```

**Passa se:**
```bash
python3 tools/validar_citacoes.py   # exit 0
```

**Teste o validador** (precisa reprovar): troque um trecho de uma citação por uma frase inventada, rode de novo, confirme `1 faltando`, e depois desfaça com `git checkout regras.md`.

**Observe e anote:**
- [ ] Quantas regras ativas, no banco e de inferência?
- [ ] Você **reconhece** a pessoa nas regras ativas? Nota de 0 a 10.
- [ ] Alguma regra é frase de efeito em vez de comportamento?

Commit.

---

## 6. Fase 4 — Portão (10 min)

Prove que a trava funciona **antes** de usar o mentor. Numa sessão do Claude Code na pasta do mentor, peça:

> Crie o arquivo teste_portao.py com um print e NÃO rode.

**Passa se** o turno não termina: o Claude Code recebe o bloqueio ("Você escreveu código e não rodou…") e roda o arquivo.

Depois peça: "agora só liste os arquivos com ls" → nenhum bloqueio. Apague `teste_portao.py`.

- [ ] Bloqueou na hora certa?
- [ ] Algum bloqueio indevido no resto do piloto? Anote cada um.

---

## 7. Fase 5 — Os 3 testes de aceitação (1–2 h)

Siga `testes/aceitacao/README.md` e registre tudo em `testes/aceitacao/RESULTADOS.md`.

**Teste 1 — Construir e ensinar.** Escolha algo do domínio que **você não domina**:
```
/<slug>-ensina <pedido>
python3 tools/validar_resposta.py testes/respostas/<arquivo>.md
```
- [ ] Validador exit 0?
- [ ] Previu antes de rodar? Mostrou uma versão quebrada de verdade?
- [ ] **Você aprendeu algo?** Escreva em 2 linhas o quê.

**Teste 2 — Revisar um script "que funciona":**
```
/<slug>-revisa testes/aceitacao/script_emoji.py
```
- [ ] Previu a quebra **antes** de rodar?
- [ ] Reproduziu com `PYTHONIOENCODING=cp1252` e mostrou o `UnicodeEncodeError`?
- [ ] Rodou original e corrigido lado a lado?

**Teste 3 — Ingestão:** um link **novo** da pessoa, que não estava no acervo:
```
/<slug>-ingere <link>
```
- [ ] Linha nova em `wiki/log.md` e página nova em `wiki/fontes/`?
- [ ] Os 3 validadores com exit 0?
- [ ] Alguma regra mudou de status?

---

## 8. Fechamento (20 min)

Preencha o placar e decida:

| Critério | Resultado |
|---|---|
| Fases 1–3 com exit 0 | ☐ |
| Portão: bloqueou certo, sem bloqueio indevido | ☐ |
| Teste 1 passou e você aprendeu algo | ☐ |
| Teste 2 previu, reproduziu e provou | ☐ |
| Teste 3 atualizou a wiki sozinho | ☐ |
| Nota "reconheço a pessoa nas regras" (0–10) | __ |
| Tempo total (humano / máquina) | __ / __ |

**Decisão:**
- **5/5 e nota ≥ 7** → o kit está validado; divulgar o piloto como caso.
- **3–4/5** → corrigir os itens do diário numa versão nova e repetir só as fases que falharam.
- **≤ 2/5** → revisar o desenho antes de divulgar.

## Diário do piloto (copie para `PILOTO-DIARIO.md`)

| hora | fase | o que aconteceu | esperado | gravidade (alta/média/baixa) | ideia de correção |
|---|---|---|---|---|---|
| | | | | | |
