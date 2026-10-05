---
name: exemplo-ingere
description: Ingestão contínua — um link, arquivo ou fala nova de Profa. Lia (personagem fictícia) entra no raw, ganha página de fonte, atualiza as páginas afetadas e pode promover regras. Use com "/exemplo-ingere <link ou arquivo>".
---

# Ingerir conteúdo novo

1. **Colete** com o coletor do tipo certo (vídeo, web, repo ou arquivo). Se já estiver no manifesto, pare e avise.
2. **Página de fonte:** crie `wiki/fontes/<id>.md` (veja o formato em /exemplo-compilar).
3. **Propague:** atualize toda página de tema, princípio ou método que o conteúdo novo toca, nos dois sentidos. Crie página nova só para conceito realmente novo.
4. **Regras:** se o conteúdo dá uma 2ª fonte a uma regra `banco`, acrescente a citação e promova para `ativa`. Se reforça uma `ativa`, acrescente a citação. Se é comportamento novo, crie como `banco`.
5. **Controle:** atualize `wiki/index.md` e `wiki/hot.md`, e acrescente uma linha em `wiki/log.md` (data, fonte, páginas tocadas, regras promovidas).
6. Rode e mostre as três saídas, todas com exit 0:
   ```
   python3 tools/stats.py && python3 tools/validar_links.py && python3 tools/validar_citacoes.py
   ```
7. Diga ao usuário, em 3–5 linhas, o que o mentor aprendeu.
