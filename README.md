# Mentor-Especialista

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

[![Mentor-Especialista](guia/assets/banner.jpg)](https://inematds.github.io/mentor-especialista/guia/)

**Kit pronto para transformar o método de um especialista num mentor dentro do Claude Code.**
O mentor ensina construindo junto, revisa antes da entrega e só diz "funciona" depois de rodar.

> Não é clone de voz nem imitação de pessoa. O kit copia o **método**: como o especialista explica, constrói, depura e verifica. Cada regra do mentor aponta para um trecho real do que a pessoa publicou.

## 📖 Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/mentor-especialista/guia/**

## Por que existe

Quando você pede a uma IA para explicar algo, ela costuma:
- explicar demais (ou de menos) e te deixar mais perdido;
- **parecer** certa sem **estar** certa;
- supor coisas sem avisar;
- responder com conhecimento genérico.

O mentor corrige isso com quatro peças:

| Peça | O que faz |
|---|---|
| **Acervo + wiki** | Tudo o que o especialista publicou, compilado numa wiki interligada que a IA consulta sem se perder |
| **Regras com prova** | Cada regra de conduta tem citação + localizador, conferidos por script; nada inventado |
| **Loop obrigatório** | Definir pronto → menor versão → prever → rodar → mostrar a versão quebrada → relatório por regra |
| **Portão de execução** | Um hook impede o turno de terminar se houve código escrito e não executado |

## Começo rápido (5 minutos)

Requisitos: Python 3.10+, git, [Claude Code](https://claude.com/claude-code). Opcional: `yt-dlp` (legendas de vídeo) e um transcritor local.

```bash
git clone https://github.com/inematds/mentor-especialista.git
cd mentor-especialista

# 1. veja o exemplo funcionando (especialista fictício, 3 fontes, 7 regras)
python3 exemplo/tools/stats.py --raiz exemplo
python3 exemplo/tools/validar_citacoes.py --raiz exemplo

# 2. crie o SEU mentor
python3 novo-mentor.py prof-redes \
  --nome "Nome do especialista" \
  --dominio "ensinar redes neurais construindo do zero" \
  --destino ~/mentores
```

Depois, dentro de `~/mentores/mentor-prof-redes/`:

1. Preencha o `ESCOPO.md` (as fontes) e ajuste o `mentor.config.json` (metas e transcritor).
2. Abra o Claude Code nessa pasta e rode, em ordem:

| Fase | Comando | Pronto quando |
|---|---|---|
| 1 Coleta | `/prof-redes-coletar` | `python3 tools/stats.py` → exit 0 |
| 2 Wiki | `/prof-redes-compilar` | `python3 tools/validar_links.py` → exit 0 |
| 3 Regras | `/prof-redes-regras` | `python3 tools/validar_citacoes.py` → exit 0 |
| 4 Uso | `/prof-redes-ensina <dúvida>` · `/prof-redes-revisa <arquivo>` | `python3 tools/validar_resposta.py <resposta>` → exit 0 |
| 5 Evolução | `/prof-redes-ingere <link>` | os três validadores → exit 0 |

3. Rode os 3 testes de aceitação em `testes/aceitacao/README.md`.

## O que vem no kit

```
novo-mentor.py            gera um mentor novo a partir do template
template/                 o projeto que cada mentor recebe
  ├── ESCOPO.md · regras.md · mentor.config.json · CLAUDE.md
  ├── raw/                acervo bruto (somente leitura depois de coletado)
  ├── wiki/               fontes · temas · principios · metodos · index · hot · log
  ├── tools/              4 coletores + 4 validadores (só biblioteca padrão)
  ├── testes/aceitacao/   3 tarefas reais, incluindo um script que "funciona" mas quebra
  └── .claude/            agente mentor · 6 skills · portão de execução + settings.json
exemplo/                  um mentor completo de um especialista FICTÍCIO, passando em tudo
docs/                     plano da solução, treinamento e guia de adaptação
tests/                    81 testes do próprio kit (pytest)
```

## Ajuste ao seu ecossistema

Tudo o que muda entre uma casa e outra fica em `mentor.config.json`:

- **Transcritor:** `transcrever_cmd` aceita qualquer comando, como Whisper local, faster-whisper ou o pipeline da sua casa. Exemplos em [docs/ADAPTAR.md](docs/ADAPTAR.md).
- **Metas de coleta:** quantos itens e palavras por tipo de fonte.
- **Seções da resposta:** os títulos que o validador exige.
- **Portão:** extensões de código, pastas ignoradas e comandos de teste por linguagem.

Fontes sem coletor automático (posts de redes sociais, PDFs, notas) entram por `coletar_arquivo.py`, a partir de uma exportação manual. **O kit não chama nenhuma API paga.**

## Atualizar um mentor que você já criou

Quando sair uma versão nova do kit, atualize o seu mentor sem perder nada:

```bash
git pull
python3 novo-mentor.py --atualizar ~/mentores/mentor-prof-redes
```

Substitui os scripts (`tools/`), o agente, as skills e o portão; acrescenta ao `mentor.config.json` só as chaves novas. **Não toca** em `raw/`, `wiki/`, `regras.md`, `ESCOPO.md` nem nas respostas. As versões anteriores ficam em `.mentor/backup-<data>/`.

## "Stop hook error occurred"? É o portão funcionando

Quando o mentor escreve código e tenta terminar sem rodar, o Claude Code mostra esse aviso. Não é defeito: é o portão de execução devolvendo o turno com o recado "Você escreveu código e não rodou". O agente roda o código e segue.

## Piloto real

O kit foi validado com um especialista de verdade: o próprio Nei, com 22 fontes públicas e 189 mil palavras. Resultado: **5 de 5** critérios e nota 8 em "reconheço a pessoa nas regras". As falhas que ele encontrou viraram as versões 1.2 e 1.3; a última delas, o mentor rodar antes de prever, só foi resolvida com um mecanismo (o portão de previsão), não com instrução. O mentor completo é público em **[inematds/mentor-nei](https://github.com/inematds/mentor-nei)**: acervo, wiki, regras, diário e resultados.

## Testar o próprio kit

```bash
python3 -m pytest -q tests     # → 81 passed
```

## Documentação

- [docs/PLANO.md](docs/PLANO.md): a solução por inteiro, as fases, os riscos e as proteções
- [docs/TREINAMENTO.md](docs/TREINAMENTO.md): plano de treinamento em 6 módulos, com rubrica
- [docs/ADAPTAR.md](docs/ADAPTAR.md): transcritores, outras linguagens, outros agentes
- [docs/PILOTO.md](docs/PILOTO.md): roteiro para levar o primeiro especialista real por todas as fases

## Uso responsável

- Use conteúdo **público** e respeite os termos de cada plataforma.
- O mentor nunca se apresenta como a pessoa nem publica texto em nome dela.
- Para uso educacional e de estudo. Para distribuir o acervo coletado, você precisa de autorização de quem o escreveu.

## Licença

MIT. Feito pela comunidade [INEMA.CLUB](https://inema.club).
