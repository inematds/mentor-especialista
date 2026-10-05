# Plano de treinamento

## Público e resultado

- **Público:** quem já usa o Claude Code no básico e quer IA que **ensina e prova**, não só gera código.
- **Ao final:** o aluno monta, com este kit, o mentor de um especialista que escolheu, com acervo, wiki, regras citadas, agente, skills, portão e os 3 testes de aceitação passando.

## Formato

- 6 módulos, 14 aulas curtas (≈15 min) + projeto final.
- Toda aula termina com uma **tarefa prática** e uma **conferência por comando**: o aluno sabe sozinho se acertou.
- Tamanho do acervo do aluno: **20–50 fontes, cerca de 50 mil palavras**. Um acervo completo é caro demais para exercício.
- Material: este repositório. O `exemplo/` serve de gabarito em todas as aulas.

## Grade

| Módulo | Aulas | Prática | Conferência |
|---|---|---|---|
| **1. Por que um mentor** | 1.1 Os 4 maus hábitos da IA ao ensinar · 1.2 Método ≠ persona: o que copiar e o que não copiar | `novo-mentor.py` + preencher `ESCOPO.md` | Domínio em 1 frase + ≥5 fontes |
| **2. Coleta do acervo** | 2.1 Fontes e coletores (legenda, transcritor local, web, repo, exportação manual) · 2.2 Subagentes em paralelo, manifesto e relatório de falhas | Coletar ≥3 tipos de fonte | `stats.py` → exit 0 |
| **3. Wiki compilada** | 3.1 Raw imutável × wiki viva · 3.2 Fontes, temas, princípios, métodos, index/hot/log | `/<slug>-compilar` | `validar_links.py` → exit 0 |
| **4. Regras com prova** | 4.1 Extrair conduta, não frases · 4.2 Citação, localizador, ativa/banco/inferência | `/<slug>-regras` (5–7 regras) | `validar_citacoes.py` → exit 0 + citação inventada reprova |
| **5. Agente, skills e portão** | 5.0 Mapa: `settings.json`, hooks, frontmatter do agente, `SKILL.md` · 5.1 Subagente com loop obrigatório · 5.2 Skills ensina/revisa/ingere · 5.3 Portão: Stop + SubagentStop | Ajustar o mentor ao domínio; provocar o portão de propósito | Portão bloqueia código não executado; `validar_resposta.py` → exit 0 |
| **6. Prova e evolução** | 6.1 Os 3 testes de aceitação · 6.2 Ingestão contínua e reuso para outro especialista | Rodar as 3 tarefas + `/<slug>-ingere` com 1 link | `RESULTADOS.md` com 3/3 + linha nova no `wiki/log.md` |

## Projeto final

O mentor completo de um especialista à escolha do aluno, com:
1. `ESCOPO.md` + `raw/MANIFESTO.json` + `raw/RELATORIO-FALHAS.md`
2. Wiki com `index`, `hot` e `log`
3. `regras.md` validado
4. Agente e skills ajustados ao domínio
5. `testes/aceitacao/RESULTADOS.md` com as 3 tarefas
6. Um vídeo curto ou print do mentor ensinando algo **que o aluno não sabia antes**

## Rubrica (10 pontos, aprovação ≥ 8)

| Critério | Pontos |
|---|---|
| Acervo rastreável (`stats.py` exit 0) | 1 |
| Wiki interligada (`validar_links.py` exit 0) | 1 |
| Regras com citação validada; inferências marcadas | 2 |
| Mentor segue o loop, comprovado por `validar_resposta.py` | 2 |
| Portão funcionando (demonstração de bloqueio + liberação) | 2 |
| 3 testes de aceitação registrados | 1 |
| Ingestão atualiza a wiki sem edição manual + demonstração | 1 |

## Trilhas por nível

- **Usar (2 h):** módulos 1 e 6 com o `exemplo/`. Aprende a perguntar, a ler o relatório por regra e a revisar antes de entregar.
- **Construir (1 semana):** grade completa + projeto final.
- **Escalar (avançado):** conselho de mentores (vários especialistas), mentor da própria marca (o criador de conteúdo como fonte), ingestão por voz (falar 10 min, a IA limpa e ingere) e porte para outros agentes ([ADAPTAR.md](ADAPTAR.md)).
