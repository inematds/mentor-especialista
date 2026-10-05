# Canal — piloto-e-cursos (só acrescentar; nunca reescrever)

Conhecimento do projeto que a compactação perde: fatos descobertos, aprendizados, glossário, armadilhas, onde estão as coisas.
Não é estado da tarefa (isso vai em state/plan/progress). Preencha cedo — o hook avisa na faixa 1 (~50% do contexto).

Formato: `- AAAA-MM-DD HH:MM · fato|aprendizado|glossário|armadilha · texto`


## 2026-10-05 15:45
- Piloto: especialista = Nei (acervo público próprio). Mentor em ~/projetos/mentor-nei (git local, sem remoto).
- Fases rodam por `claude -p "/nei-<fase>" --dangerously-skip-permissions --output-format stream-json --verbose` dentro do mentor, com systemd-run MemoryMax=16G + timeout. Logs em mentor-nei/logs/faseN.jsonl.
- coletar_video.py com legenda automática pt funcionou isolado (9540 palavras em 1 live).
- Armadilha: tipo do manifesto "video" e pasta raw/videos (plural) — não quebra, só inconsistente.
