# Mentor-Especialista

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

[![Expert Mentor](guia/assets/banner-en.jpg)](https://inematds.github.io/mentor-especialista/guia/en/)

**A ready-made kit to turn an expert's method into a mentor inside Claude Code.**
The mentor teaches by building together with you, reviews before delivering, and only says "it works" after running it.

> This is not a voice clone or an impersonation. The kit copies the **method**: how the expert explains, builds, debugs, and verifies. Every mentor rule points to a real passage of what the person has published.

## 📖 User guide

Full guide (landing page + step by step): **https://inematds.github.io/mentor-especialista/guia/en/**

## Why it exists

When you ask an AI to explain something, it tends to:
- explain too much (or too little) and leave you more lost;
- **seem** right without **being** right;
- make assumptions without telling you;
- answer with generic knowledge.

The mentor fixes this with four pieces:

| Piece | What it does |
|---|---|
| **Corpus + wiki** | Everything the expert has published, compiled into an interlinked wiki that the AI can consult without getting lost |
| **Rules with proof** | Every conduct rule has a quote + locator, checked by script; nothing made up |
| **Mandatory loop** | Define done → smallest version → predict → run → show the broken version → report per rule |
| **Execution gate** | A hook prevents the turn from ending if code was written but not executed |

## Quick start (5 minutes)

Requirements: Python 3.10+, git, [Claude Code](https://claude.com/claude-code). Optional: `yt-dlp` (video subtitles) and a local transcriber.

```bash
git clone https://github.com/inematds/mentor-especialista.git
cd mentor-especialista

# 1. see the example working (fictional expert, 3 sources, 7 rules)
python3 exemplo/tools/stats.py --raiz exemplo
python3 exemplo/tools/validar_citacoes.py --raiz exemplo

# 2. create YOUR mentor
python3 novo-mentor.py prof-redes \
  --nome "Expert's name" \
  --dominio "teach neural networks by building from scratch" \
  --destino ~/mentores
```

Then, inside `~/mentores/mentor-prof-redes/`:

1. Fill in `ESCOPO.md` (the sources) and adjust `mentor.config.json` (targets and transcriber).
2. Open Claude Code in that folder and run, in order:

| Phase | Command | Done when |
|---|---|---|
| 1 Collection | `/prof-redes-coletar` | `python3 tools/stats.py` → exit 0 |
| 2 Wiki | `/prof-redes-compilar` | `python3 tools/validar_links.py` → exit 0 |
| 3 Rules | `/prof-redes-regras` | `python3 tools/validar_citacoes.py` → exit 0 |
| 4 Use | `/prof-redes-ensina <question>` · `/prof-redes-revisa <file>` | `python3 tools/validar_resposta.py <answer>` → exit 0 |
| 5 Evolution | `/prof-redes-ingere <link>` | all three validators → exit 0 |

3. Run the 3 acceptance tests in `testes/aceitacao/README.md`.

## What comes in the kit

```
novo-mentor.py            generates a new mentor from the template
template/                 the project each mentor receives
  ├── ESCOPO.md · regras.md · mentor.config.json · CLAUDE.md
  ├── raw/                raw corpus (read-only once collected)
  ├── wiki/               fontes · temas · principios · metodos · index · hot · log
  ├── tools/              4 collectors + 4 validators (standard library only)
  ├── testes/aceitacao/   3 real tasks, including a script that "works" but is broken
  └── .claude/            mentor agent · 6 skills · execution gate + settings.json
exemplo/                  a complete mentor of a FICTIONAL expert, passing everything
docs/                     solution plan, training, and adaptation guide
tests/                    56 tests of the kit itself (pytest)
```

## Adapt it to your ecosystem

Everything that changes from one setup to another lives in `mentor.config.json`:

- **Transcriber:** `transcrever_cmd` accepts any command, such as local Whisper, faster-whisper, or your own pipeline. Examples in [docs/ADAPTAR.md](docs/ADAPTAR.md) (in Portuguese).
- **Collection targets:** how many items and words per source type.
- **Answer sections:** the headings the validator requires.
- **Gate:** code extensions, ignored folders, and test commands per language.

Sources without an automatic collector (social media posts, PDFs, notes) come in through `coletar_arquivo.py`, from a manual export. **The kit does not call any paid API.**

## Test the kit itself

```bash
python3 -m pytest -q tests     # → 56 passed
```

## Documentation

- [docs/PLANO.md](docs/PLANO.md) (in Portuguese): the whole solution, the phases, the risks, and the safeguards
- [docs/TREINAMENTO.md](docs/TREINAMENTO.md) (in Portuguese): a 6-module training plan, with rubric
- [docs/ADAPTAR.md](docs/ADAPTAR.md) (in Portuguese): transcribers, other languages, other agents
- [docs/PILOTO.md](docs/PILOTO.md) (in Portuguese): roadmap for taking the first real expert through all the phases

## Responsible use

- Use **public** content and respect each platform's terms.
- The mentor never presents itself as the person nor publishes text on their behalf.
- For educational and study purposes. To distribute the collected corpus, you need authorization from whoever wrote it.

## License

MIT. Made by the [INEMA.CLUB](https://inema.club) community.
