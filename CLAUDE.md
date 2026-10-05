# CLAUDE.md — kit mentor-especialista

Kit da comunidade para criar mentores no Claude Code. Repo público: `inematds/mentor-especialista` (autor dos commits: `inematds <inematds@gmail.com>`).

## Regras do repo

- `template/` é a fonte. `exemplo/` foi gerado dele: ao mudar `template/tools/*` ou `template/.claude/hooks|settings.json`, copie para `exemplo/` (o `test_exemplo_em_dia_com_template` cobra).
- Só biblioteca padrão do Python nos scripts. `pytest` só para os testes do kit.
- Nada específico de uma casa (caminhos pessoais, ferramentas internas) no template. Integração vai para `docs/ADAPTAR.md` como exemplo.
- Nenhuma API paga no kit.
- Antes de commitar: `python3 -m pytest -q tests` → tudo passando.
- Versão em `VERSION` + `CHANGELOG.md` (semver: o minor carrega o patch, só o major zera).

## Self-learning

Quando eu te corrigir, ou você perceber um erro seu: antes de continuar, registre a lição como uma regra de uma linha em ## Lessons.

## Lessons
