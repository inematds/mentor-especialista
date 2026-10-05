# Plano da solução

## A ideia em uma frase

Transformar o **modo de pensar** de um especialista, tirado do que ele publicou, num agente que **ensina e revisa como ele**, segue regras comprovadas por citação e só responde depois de rodar o código que escreveu.

A IA pode fazer o trabalho pesado, mas compreender continua sendo tarefa de quem usa. O mentor existe para o usuário **entender**, não só para receber código pronto.

## Arquitetura: 6 camadas

```
 1. ACERVO BRUTO       raw/<tipo>/…  + MANIFESTO.json (sha256) + RELATORIO-FALHAS.md
 2. WIKI COMPILADA     wiki/ fontes · temas · principios · metodos · index · hot · log
 3. REGRAS             regras.md — citação + localizador; ativa / banco / inferencia
 4. AGENTE + SKILLS    <slug>-mentor · coletar · compilar · regras · ensina · revisa · ingere
 5. PORTÃO             hook: código escrito e não executado → turno bloqueado
 6. INGESTÃO CONTÍNUA  1 link novo → fonte + páginas afetadas + regras promovidas + log
```

## Fases e critérios de pronto

| Fase | O que faz | Arquivos do kit | Pronto quando |
|---|---|---|---|
| 0 Escopo | Escolher especialista, domínio estreito e fontes | `ESCOPO.md`, `mentor.config.json` | Domínio em 1 frase, ≥5 fontes listadas, metas definidas |
| 1 Coleta | Um subagente por fonte, em paralelo; nada pago | `tools/coletar_*.py`, skill `coletar` | `stats.py` → exit 0: metas por tipo batidas, 0 item sem hash, raw intacto, relatório de falhas presente |
| 2 Wiki | Compilar o raw (somente leitura) em páginas ligadas nos dois sentidos | skill `compilar` | `validar_links.py` → exit 0: 0 links quebrados, toda fonte com link, todo princípio com fonte, nº de fontes = manifesto |
| 3 Regras | Extrair condutas recorrentes com trecho copiado do raw | skill `regras` | `validar_citacoes.py` → exit 0, e uma citação inventada **reprova** |
| 4 Agente | Loop obrigatório + skills de ensino e revisão | `.claude/agents`, skills `ensina`/`revisa` | `validar_resposta.py` → exit 0 (seções, regras existentes, ≥1 execução no transcript) |
| 5 Portão | PostToolUse marca/limpa, Stop e SubagentStop bloqueiam | `.claude/hooks`, `.claude/settings.json` | testes do portão passando (`tests/test_portao.py` no kit) |
| 6 Aceitação | 3 tarefas reais | `testes/aceitacao/` | As 3 registradas em `RESULTADOS.md` |
| 7 Operação | Ingestão contínua e revisão mensal | skill `ingere` | Os três validadores → exit 0 após cada ingestão |

## O loop do mentor

1. **Pronto:** o que é "terminado", antes de tocar no código.
2. **Menor versão:** a peça mínima que roda, uma coisa de cada vez.
3. **Previsão:** o resultado esperado, dito antes de rodar.
4. **Saída real:** rodar de verdade e comparar.
5. **Versão quebrada:** mostrar uma variação que quebra, explicar a causa, corrigir.
6. **Relatório:** passo → o que rodou → o que saiu → regra que guiou.

## Regras: como se tornam confiáveis

- Regra = comportamento recorrente, não frase de efeito.
- Cada citação é um **trecho copiado** do raw + localizador (`arquivo@tempo` ou `arquivo#linha`).
- `ativa` exige ≥2 arquivos diferentes; `banco` espera a 2ª fonte; `inferencia` é avisada ao usuário.
- O validador compara texto normalizado (caixa, acento, pontuação), porque transcrição nunca é literal.

## O portão de execução

| Evento | Ação |
|---|---|
| `PostToolUse` Write/Edit/MultiEdit | arquivo de código fora de `raw/`/`wiki/`/`docs/` → "sujo" |
| `PostToolUse` Bash | limpa só o que o comando executa (nome do arquivo, `-m modulo`, executor de testes da linguagem) |
| `Stop` / `SubagentStop` | sujo → `{"decision":"block","reason":…}` |
| `stop_hook_active=true` | sai 0 (no máximo 1 bloqueio por turno, sem loop) |
| erro interno | sai 0 (o portão nunca derruba a sessão) |

O estado fica em `.mentor/estado/<session_id>.json`. O portão não depende do formato do transcript.

## Riscos e proteções

| Risco | Proteção |
|---|---|
| Citação inventada | Busca normalizada no raw + teste negativo |
| Regra com base fraca | Promoção só com ≥2 fontes; `inferencia` explícita |
| Raw "corrigido" depois | `stats.py` confere o sha256 de cada item |
| Hook em loop ou atrapalhando outros projetos | Registro só no `.claude/settings.json` do projeto + `stop_hook_active` |
| Portão que não pega o subagente | Também registrado em `SubagentStop` |
| Wiki grande demais para o contexto | Entrada por `hot.md` → `index.md`; subagente com contexto próprio |
| Imitar a pessoa | Mentor de método, nunca de persona; nada publicado em nome dela |
| Custo escondido | Nenhuma API paga no kit; coleta manual entra por `coletar_arquivo.py` |
| Transcrição travando a máquina | `transcrever_cmd` com teto de memória + `timeout_video_s` |

## Esforço

| Fase | Duração típica |
|---|---|
| Escopo | ½ dia |
| Coleta | 1–2 dias (horas de máquina se precisar transcrever; minutos se houver legenda) |
| Wiki | 1 dia |
| Regras | ½–1 dia |
| Agente, skills e portão | já vêm no kit (ajustes: ½ dia) |
| Aceitação | ½ dia |
| **Total** | **≈ 4–5 dias** para o primeiro mentor; o segundo sai bem mais rápido |
