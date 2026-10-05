# Mentor-Especialista

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

[![Mentor Experto](guia/assets/banner-es.jpg)](https://inematds.github.io/mentor-especialista/guia/es/)

**Kit listo para convertir el método de un experto en un mentor dentro de Claude Code.**
El mentor enseña construyendo contigo, revisa antes de entregar y solo dice "funciona" después de ejecutar.

> No es un clon de voz ni una imitación de persona. El kit copia el **método**: cómo el experto explica, construye, depura y verifica. Cada regla del mentor apunta a un fragmento real de lo que la persona publicó.

## 📖 Guía de uso

Guía completa (landing + paso a paso): **https://inematds.github.io/mentor-especialista/guia/es/**

## Por qué existe

Cuando le pides a una IA que explique algo, suele:
- explicar de más (o de menos) y dejarte más perdido;
- **parecer** correcta sin **estar** correcta;
- suponer cosas sin avisar;
- responder con conocimiento genérico.

El mentor corrige esto con cuatro piezas:

| Pieza | Qué hace |
|---|---|
| **Acervo + wiki** | Todo lo que el experto publicó, compilado en una wiki interconectada que la IA consulta sin perderse |
| **Reglas con prueba** | Cada regla de conducta tiene cita + localizador, verificados por script; nada inventado |
| **Loop obligatorio** | Definir listo → versión mínima → predecir → ejecutar → mostrar la versión rota → informe por regla |
| **Puerta de ejecución** | Un hook impide que el turno termine si se escribió código y no se ejecutó |

## Inicio rápido (5 minutos)

Requisitos: Python 3.10+, git, [Claude Code](https://claude.com/claude-code). Opcional: `yt-dlp` (subtítulos de video) y un transcriptor local.

```bash
git clone https://github.com/inematds/mentor-especialista.git
cd mentor-especialista

# 1. mira el ejemplo funcionando (experto ficticio, 3 fuentes, 7 reglas)
python3 exemplo/tools/stats.py --raiz exemplo
python3 exemplo/tools/validar_citacoes.py --raiz exemplo

# 2. crea TU mentor
python3 novo-mentor.py prof-redes \
  --nome "Nombre del experto" \
  --dominio "enseñar redes neuronales construyendo desde cero" \
  --destino ~/mentores
```

Después, dentro de `~/mentores/mentor-prof-redes/`:

1. Completa `ESCOPO.md` (las fuentes) y ajusta `mentor.config.json` (metas y transcriptor).
2. Abre Claude Code en esa carpeta y ejecuta, en orden:

| Fase | Comando | Listo cuando |
|---|---|---|
| 1 Recolección | `/prof-redes-coletar` | `python3 tools/stats.py` → exit 0 |
| 2 Wiki | `/prof-redes-compilar` | `python3 tools/validar_links.py` → exit 0 |
| 3 Reglas | `/prof-redes-regras` | `python3 tools/validar_citacoes.py` → exit 0 |
| 4 Uso | `/prof-redes-ensina <duda>` · `/prof-redes-revisa <archivo>` | `python3 tools/validar_resposta.py <respuesta>` → exit 0 |
| 5 Evolución | `/prof-redes-ingere <enlace>` | los tres validadores → exit 0 |

3. Ejecuta las 3 pruebas de aceptación en `testes/aceitacao/README.md`.

## Qué incluye el kit

```
novo-mentor.py            genera un mentor nuevo a partir de la plantilla
template/                 el proyecto que recibe cada mentor
  ├── ESCOPO.md · regras.md · mentor.config.json · CLAUDE.md
  ├── raw/                acervo en bruto (solo lectura una vez recolectado)
  ├── wiki/               fontes · temas · principios · metodos · index · hot · log
  ├── tools/              4 recolectores + 4 validadores (solo biblioteca estándar)
  ├── testes/aceitacao/   3 tareas reales, incluido un script que "funciona" pero está roto
  └── .claude/            agente mentor · 6 skills · puerta de ejecución + settings.json
exemplo/                  un mentor completo de un experto FICTICIO, que pasa todo
docs/                     plan de la solución, entrenamiento y guía de adaptación
tests/                    81 pruebas del propio kit (pytest)
```

## Ajústalo a tu ecosistema

Todo lo que cambia de un entorno a otro está en `mentor.config.json`:

- **Transcriptor:** `transcrever_cmd` acepta cualquier comando, como Whisper local, faster-whisper o el pipeline de tu casa. Ejemplos en [docs/ADAPTAR.md](docs/ADAPTAR.md) (en portugués).
- **Metas de recolección:** cuántos ítems y palabras por tipo de fuente.
- **Secciones de la respuesta:** los títulos que exige el validador.
- **Puerta:** extensiones de código, carpetas ignoradas y comandos de prueba por lenguaje.

Las fuentes sin recolector automático (publicaciones de redes sociales, PDFs, notas) entran por `coletar_arquivo.py`, a partir de una exportación manual. **El kit no llama a ninguna API de pago.**

## Actualizar un mentor que ya creaste

Cuando salga una versión nueva del kit, actualiza tu mentor sin perder nada:

```bash
git pull
python3 novo-mentor.py --atualizar ~/mentores/mentor-prof-redes
```

Reemplaza los scripts (`tools/`), el agente, las skills y la puerta, y agrega a `mentor.config.json` solo las claves nuevas. **No toca** `raw/`, `wiki/`, `regras.md`, `ESCOPO.md` ni las respuestas guardadas. Las versiones anteriores quedan en `.mentor/backup-<fecha>/`.

## ¿"Stop hook error occurred"? Es la puerta funcionando

Cuando el mentor escribe código e intenta terminar sin ejecutarlo, Claude Code muestra este aviso. No es un defecto: es la puerta de ejecución devolviendo el turno con el mensaje "Escribiste código y no lo ejecutaste". El agente ejecuta el código y sigue.

## Piloto real

El kit se validó con un experto de verdad: el propio Nei, con 22 fuentes públicas y 189 mil palabras. Resultado: **5 de 5** criterios y nota 8 en "reconozco a la persona en las reglas". Las fallas que encontró se convirtieron en las versiones 1.2 y 1.3; la última, que el mentor ejecutara antes de predecir, solo se resolvió con un mecanismo (la puerta de predicción), no con instrucciones. El mentor completo es público en **[inematds/mentor-nei](https://github.com/inematds/mentor-nei)** (en portugués): acervo, wiki, reglas, diario y resultados.

## Probar el propio kit

```bash
python3 -m pytest -q tests     # → 81 passed
```

## Documentación

- [docs/PLANO.md](docs/PLANO.md) (en portugués): la solución completa, las fases, los riesgos y las protecciones
- [docs/TREINAMENTO.md](docs/TREINAMENTO.md) (en portugués): plan de entrenamiento en 6 módulos, con rúbrica
- [docs/ADAPTAR.md](docs/ADAPTAR.md) (en portugués): transcriptores, otros lenguajes, otros agentes
- [docs/PILOTO.md](docs/PILOTO.md) (en portugués): guía para llevar al primer experto real por todas las fases

## Uso responsable

- Usa contenido **público** y respeta los términos de cada plataforma.
- El mentor nunca se presenta como la persona ni publica texto en su nombre.
- Para uso educativo y de estudio. Para distribuir el acervo recolectado, necesitas autorización de quien lo escribió.

## Licencia

MIT. Hecho por la comunidad [INEMA.CLUB](https://inema.club).
