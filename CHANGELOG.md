# Changelog

## 1.2.0 — 2026-10-05

Correções vindas do piloto real (mentor do Nei: 22 fontes, 189 mil palavras, 4/5, nota 8; diário em inematds/mentor-nei).

- Manifesto com trava de arquivo e escrita atômica: coleta com um subagente por fonte em paralelo não perde itens.
- Vídeo salvo com título + ID (antes, a transcrição local virava `transcript.txt` e sobrescrevia a anterior).
- Legenda agrupada em parágrafos de cerca de 30 s; o validador ignora `[hh:mm:ss]`, então citações que cruzam linhas são encontradas.
- `validar_resposta.py`: perfil `--perfil revisao`; com `--transcript`, confere se a previsão veio ANTES da primeira execução, lendo também as transcrições dos subagentes.
- O agente inclui as seções pedidas pelas regras do especialista ("no mentor:"), e `/regras` as acrescenta a `secoes_resposta`.
- Revisão em 5 seções (Previsão → Reprodução → Correção → Lado a lado → Relatório); arquivo `<nome>.revisado.<ext>`; temporários em `.mentor/tmp/`; resposta no idioma do pedido.
- `stats.py` diz quanto falta para cada meta.
- `novo-mentor.py --atualizar PASTA` leva um mentor existente para a versão nova sem tocar no conteúdo.
- README: o aviso "Stop hook error occurred" é o portão funcionando. 70 testes.

**Limitação conhecida (vai para a 1.3):** mesmo instruído a escrever `Previsão:` antes de executar, o mentor tende a prever só no raciocínio e escrever depois. O `validar_resposta --transcript` detecta isso (reprovou as rodadas 2 e 3 do teste 2 do piloto); a correção prevista é um portão de previsão (PreToolUse em Bash).

## 1.1.0 — 2026-10-05

- Guia landing PT/EN/ES em `guia/` (GitHub Pages), READMEs EN/ES, capa do catálogo.
- `docs/PILOTO.md`: roteiro do primeiro mentor real.

## 1.0.0 — 2026-10-05

- Gerador `novo-mentor.py` e template completo: escopo, raw, wiki, regras e config.
- Coletores: vídeo (legenda → transcritor plugável), web, repositório, arquivo/exportação manual.
- Validadores: `stats.py` (metas + integridade sha256), `validar_links.py`, `validar_citacoes.py` (normalizado, ativa/banco/inferência), `validar_resposta.py` (seções, regras, execução no transcript).
- Agente mentor com loop obrigatório e 6 skills: coletar, compilar, regras, ensina, revisa, ingere.
- Portão de execução (PostToolUse + Stop + SubagentStop, estado por sessão, anti-loop).
- Exemplo completo de especialista fictício; 3 testes de aceitação; 56 testes do kit (inclui regressões da verificação: escape de nome/domínio, portão sem falsos positivos, `<pre>` preservado, só http/https).
- Docs: plano, treinamento (6 módulos, rubrica) e guia de adaptação.
