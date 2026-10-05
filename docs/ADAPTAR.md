# Adaptar o kit ao seu ecossistema

## 1. Transcritor de vídeo

O `coletar_video.py` tenta primeiro a **legenda que já existe** (com `yt-dlp --skip-download`, sem baixar o vídeo). Se não houver legenda, ele usa o seu transcritor, definido em `mentor.config.json`:

```json
"transcrever_cmd": "<comando com {url} e {saida}>"
```

O comando precisa deixar um `.vtt`, `.srt` ou `.txt` dentro de `{saida}`. Exemplos:

**Whisper (openai-whisper, local):**
```json
"transcrever_cmd": "yt-dlp -x --audio-format mp3 -o {saida}/a.%(ext)s {url} && whisper {saida}/a.mp3 --model medium --output_format vtt --output_dir {saida}"
```

**faster-whisper (via script seu):**
```json
"transcrever_cmd": "python3 ~/bin/transcreve.py --url {url} --out {saida}"
```

**Pipeline próprio, com teto de memória (Linux, systemd):**
```json
"transcrever_cmd": "systemd-run --user --scope -p MemoryMax=24G -- python3 ~/meu-pipeline/transcrever.py --url {url} --outdir {saida}"
```

Transcrição é pesada: sempre use um teto de memória e o `timeout_video_s`.

## 2. Fontes sem coletor

| Fonte | Como entra |
|---|---|
| Posts de redes sociais | Exporte pelo próprio site (arquivo de dados da conta) ou copie para `.txt` → `coletar_arquivo.py --tipo posts` |
| PDF / livro | Converta para texto (ex.: `pdftotext`) → `coletar_arquivo.py --tipo livro` |
| Palestra presencial | Grave e transcreva localmente → `coletar_arquivo.py --tipo palestras` |
| Newsletter | `coletar_web.py --tipo newsletter` ou exportação |

Existem APIs pagas de terceiros para coletar posts em massa. O kit **não** as usa: se você optar por uma, ela é decisão sua, e o resultado entra pelo `coletar_arquivo.py`.

## 3. Outras linguagens no portão

Em `mentor.config.json` → `portao`, você pode sobrescrever:

```json
"portao": {
  "extensoes_codigo": [".py", ".ex", ".exs"],
  "pastas_ignoradas": ["raw", "wiki", "docs", ".claude", ".mentor"],
  "executores_teste": { ".ex": ["mix test", "mix run"], ".exs": ["mix test"] }
}
```

O portão libera um arquivo quando um comando Bash o executa (cita o nome dele, ou o roda como módulo com `-m`) **ou** quando roda o executor de testes da linguagem. `ls`, `cat`, `grep` e `git diff` não contam como execução.

## 4. Mentores que não ensinam código

Para vendas, escrita, coaching etc., troque o loop em `.claude/agents/<slug>-mentor.md` e as `secoes_resposta` no config. Exemplo para escrita:

```json
"secoes_resposta": ["Objetivo", "Rascunho mínimo", "Previsão de reação", "Teste com leitor", "Versão fraca", "Relatório"]
```

O portão continua útil se o mentor gerar scripts. Se não gerar, ele simplesmente nunca bloqueia.

## 5. Outros agentes (Codex, Gemini CLI, Cursor…)

O núcleo (`raw/`, `wiki/`, `regras.md`, `tools/`) é independente de agente. Para portar:

1. Copie o corpo de `.claude/agents/<slug>-mentor.md` para o arquivo de instruções do seu agente (ex.: `AGENTS.md`).
2. Transforme cada `SKILL.md` em comando ou prompt salvo do seu agente.
3. O portão depende de hooks no fim do turno. Sem isso, rode `validar_resposta.py --transcript` depois de cada resposta.

## 6. Vários mentores (conselho)

**Atenção ao caminho.** O agente lê `regras.md`, `wiki/hot.md` e `wiki/index.md` por caminho **relativo à pasta do mentor**. Copiar só o `.claude/agents/<slug>-mentor.md` para outro projeto deixa o mentor sem o núcleo dele: ele responde no genérico e as citações quebram.

Duas formas que funcionam:

1. **Rodar cada mentor na pasta dele.** O seu projeto chama o mentor com `claude -p "/<slug>-ensina …"` executado em `~/mentores/mentor-<slug>`.
2. **Agente local que aponta para a pasta.** No seu projeto, crie `.claude/agents/<slug>-mentor.md` com o mesmo texto do original e, no começo, diga onde está o núcleo:
   ```
   O núcleo deste mentor está em ~/mentores/mentor-<slug>/: leia regras.md, wiki/hot.md e wiki/index.md
   de lá, e só as páginas de wiki/ que precisar. Nunca invente regra que não esteja nesse regras.md.
   ```

Depois disso, no seu projeto: "consulte o mentor A e o mentor B e compare". Cada um continua preso às próprias regras e citações.
