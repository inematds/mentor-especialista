# Changelog

## 1.0.0 — 2026-10-05

- Gerador `novo-mentor.py` e template completo: escopo, raw, wiki, regras e config.
- Coletores: vídeo (legenda → transcritor plugável), web, repositório, arquivo/exportação manual.
- Validadores: `stats.py` (metas + integridade sha256), `validar_links.py`, `validar_citacoes.py` (normalizado, ativa/banco/inferência), `validar_resposta.py` (seções, regras, execução no transcript).
- Agente mentor com loop obrigatório e 6 skills: coletar, compilar, regras, ensina, revisa, ingere.
- Portão de execução (PostToolUse + Stop + SubagentStop, estado por sessão, anti-loop).
- Exemplo completo de especialista fictício; 3 testes de aceitação; 36 testes do kit.
- Docs: plano, treinamento (6 módulos, rubrica) e guia de adaptação.
