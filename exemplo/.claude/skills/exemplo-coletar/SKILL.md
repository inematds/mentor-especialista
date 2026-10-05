---
name: exemplo-coletar
description: Fase 1 — coleta o acervo público de Profa. Lia (personagem fictícia) listado em ESCOPO.md para raw/, um subagente por fonte em paralelo, e confere as metas. Use com "/exemplo-coletar" ou "coletar o acervo".
---

# Coletar o acervo

1. Leia `ESCOPO.md` (lista de fontes) e `mentor.config.json` (metas, idiomas, transcritor).
2. **Um subagente por fonte, em paralelo.** Cada um usa só o coletor do seu tipo:
   - vídeo: `python3 tools/coletar_video.py <URL>...`
   - página/blog: `python3 tools/coletar_web.py <URL>... --tipo blog`
   - repositório: `python3 tools/coletar_repo.py <URL>...`
   - exportação manual (posts, notas): `python3 tools/coletar_arquivo.py <arquivos> --tipo posts --origem "..."`
3. **Nenhuma API paga** sem autorização explícita do dono do projeto (serviço + finalidade). Na falta dela, registre a fonte como falha e siga com o resto.
4. Nunca edite um arquivo em `raw/` depois de coletado. O `stats.py` detecta a mudança pelo sha256.
5. No fim, rode e mostre a saída:
   ```
   python3 tools/stats.py
   ```
   Pronto = exit 0. Se reprovar, mostre o motivo e o que falta coletar. Liste também as linhas de `raw/RELATORIO-FALHAS.md` para conferência manual.
