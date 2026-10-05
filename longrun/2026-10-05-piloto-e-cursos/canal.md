# Canal — piloto-e-cursos (só acrescentar; nunca reescrever)

Conhecimento do projeto que a compactação perde: fatos descobertos, aprendizados, glossário, armadilhas, onde estão as coisas.
Não é estado da tarefa (isso vai em state/plan/progress). Preencha cedo — o hook avisa na faixa 1 (~50% do contexto).

Formato: `- AAAA-MM-DD HH:MM · fato|aprendizado|glossário|armadilha · texto`


## 2026-10-05 15:45
- Piloto: especialista = Nei (acervo público próprio). Mentor em ~/projetos/mentor-nei (git local, sem remoto).
- Fases rodam por `claude -p "/nei-<fase>" --dangerously-skip-permissions --output-format stream-json --verbose` dentro do mentor, com systemd-run MemoryMax=16G + timeout. Logs em mentor-nei/logs/faseN.jsonl.
- coletar_video.py com legenda automática pt funcionou isolado (9540 palavras em 1 live).
- Armadilha: tipo do manifesto "video" e pasta raw/videos (plural) — não quebra, só inconsistente.

## 2026-10-05 18:00
- Lição: instrução "escreva Previsão: antes" não muda o comportamento do subagente (2 rodadas). Precisa de mecanismo (PreToolUse). Material de aula.
- Lição: a sessão principal diz "validador passa" rodando sem --transcript; o validador externo com log reprova. Verificação tem que vir de fora.
- Transcrições de subagentes: ~/.claude/projects/<proj>/<sessão>/subagents/agent-*.jsonl (o stream-json da sessão não traz os textos do subagente).
- Erro meu: git checkout num arquivo não commitado apagou as regras da fase 3; recuperado do log (FALHAS.md do mentor-nei + Lesson no wifi/CLAUDE.md).

## Backlog kit 1.3 (achados durante o curso)
- portão de previsão (PreToolUse em Bash): instrução não bastou no teste 2.
- validar_links.py não confere link nos dois sentidos (fonte↔conceito): 3 ligações de mão única no mentor-nei passam com exit 0 (achado da trilha 3).

## 2026-10-05 17:15 — checkpoint de contexto (50%)
- Curso v2: ~/projetos/mentor-especialista-curso → repo inematds/mentor-especialista-curso (47fc080), Pages via Actions em https://inematds.github.io/mentor-especialista-curso/. Falta trilha5/index.html (subagente escrevendo); depois: novo push.
- learn.css do curso ganhou correções de celular (nav em 2ª linha com rolagem; code/font-mono/flex-1 quebram). Falta: h2 longo no 5-1 (432px).
- Portal: outra sessão publicando "INEMA Agent Runtime" (id 312) com Portal.tsx/courses.ts sujos. NÃO misturar: vigia espera-portal.sh no scratchpad; meu curso entra com id = MAX+1 depois que ela commitar. Diff da outra sessão salvo em scratchpad/portal-outra-sessao.diff.
- v6: skill formato-curso-v6 só por invocação do usuário (/formato-curso-v6); não replicar.
- Portão de previsão (1.3): PreToolUse recebe agent_id/agent_type quando o Bash vem de subagente; transcript_path é o da sessão principal. Ideia: ler a transcrição do subagente em <sessão>/subagents/agent-<agent_id>.jsonl.
- Pendências "resolva os problemas": portão de previsão; validar_links ida-e-volta; ADAPTAR.md (caminho relativo de regras/wiki); mentor-nei wiki/log.md diz 15 vídeos/6 guias (real 14/7).
