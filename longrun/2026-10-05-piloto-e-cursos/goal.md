# Goal — piloto-e-cursos

- **Início:** 2026-10-05 15:37 · **Agente:** Claude Code (sessão interativa)
- **Tetos:** tempo 10 h · memória por processo pesado 24 G (systemd-run) · sem API paga

## Resultado
Piloto real do kit feito com um especialista de verdade (o Nei, acervo público dele), kit corrigido a partir do diário do piloto e publicado, e dois cursos sobre o kit (formato v2 e formato v6) publicados e cadastrados no portal.

## Critérios de pronto (verificáveis)

**Função**
- [ ] `cd ~/projetos/mentor-nei && python3 tools/stats.py` → exit 0, com TOTAL ≥ 15 itens e ≥ 30000 palavras
- [ ] `python3 tools/validar_links.py` → exit 0 (nº de fontes = manifesto)
- [ ] `python3 tools/validar_citacoes.py` → exit 0, com ≥ 5 regras e ≥ 3 ativas
- [ ] teste negativo: citação inventada → `1 faltando`, exit 1 (desfeito depois)
- [ ] portão provado numa sessão real `claude -p` (bloqueio registrado em PILOTO-DIARIO.md com trecho da saída)
- [ ] `python3 tools/validar_resposta.py testes/respostas/<teste1>.md --transcript <jsonl>` → exit 0
- [ ] `testes/aceitacao/RESULTADOS.md` com 3 linhas preenchidas (passou/não + evidência)
- [ ] `PILOTO-DIARIO.md` com placar preenchido
- [ ] kit: `git -C ~/projetos/mentor-especialista ls-remote origin main` = HEAD local, VERSION ≥ 1.2, CHANGELOG cita o piloto
- [ ] curso v2: `curl -s -o /dev/null -w '%{http_code}' <url>` → 200; skill revisar-curso sem erro bloqueante
- [ ] curso v6: `node auditar-curso.cjs` (da skill v6) → aprovado; URL → 200
- [ ] portal: os dois cursos em `platformsData` + `updatesData` (push feito)

**Regressão**
- [ ] `cd ~/projetos/mentor-especialista && python3 -m pytest -q tests` → todos passam (≥ 56)
- [ ] validadores do `exemplo/` → exit 0

**Limite**
- [ ] nenhuma chamada de API paga (só assinatura Claude/Codex)
- [ ] nada no Vercel; push = fim
- [ ] no portal, commitar só as próprias linhas (working tree de outra sessão não entra)

**Teste rápido por ciclo:** `python3 -m pytest -q tests` (kit) / validadores do mentor-nei
**Teste completo no final:** todos os critérios acima

## Restrições
- só pela assinatura (sem API sem autorização)
- acervo do piloto = conteúdo público do próprio Nei (lives YouTube @inematdsx, guias inematds.github.io)
- não mexer em: repos de outros projetos além de portal/inemabuscas/inemapro-mono via skill atualiza-portal

## Portões humanos (parar e perguntar)
- gasto de crédito / API / render pago
- decisão de negócio ou conflito entre requisitos
- (push de kit, cursos e portal: autorizado pelo usuário em 05/10 — "pode publicar e criar tudo", "faça o piloto e depois o curso")
