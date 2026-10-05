"""Validadores: passam no exemplo e reprovam quando deveriam (sem atalho)."""
import json
import shutil

import pytest
from conftest import EXEMPLO, rodar

TOOLS = EXEMPLO / "tools"


@pytest.fixture
def copia(tmp_path):
    destino = tmp_path / "m"
    shutil.copytree(EXEMPLO, destino, ignore=shutil.ignore_patterns(".mentor", "__pycache__"))
    return destino


def test_exemplo_passa_nas_tres_fases():
    for script in ("stats.py", "validar_links.py", "validar_citacoes.py"):
        r = rodar(TOOLS / script, "--raiz", EXEMPLO)
        assert r.returncode == 0, f"{script}\n{r.stdout}"


def test_stats_reprova_manifesto_vazio(copia):
    (copia / "raw" / "MANIFESTO.json").write_text("[]")
    r = rodar(copia / "tools" / "stats.py", "--raiz", copia)
    assert r.returncode == 1 and "manifesto vazio" in r.stdout


def test_stats_reprova_raw_alterado(copia):
    arq = copia / "raw" / "blog" / "post-dizer-que-funciona.md"
    arq.write_text(arq.read_text() + "\nlinha nova\n")
    r = rodar(copia / "tools" / "stats.py", "--raiz", copia)
    assert r.returncode == 1 and "sha256 diferente" in r.stdout


def test_stats_reprova_meta_nao_batida(copia):
    cfg = json.loads((copia / "mentor.config.json").read_text())
    cfg["metas_coleta"]["video"] = {"itens": 50, "palavras": 1}
    (copia / "mentor.config.json").write_text(json.dumps(cfg))
    assert rodar(copia / "tools" / "stats.py", "--raiz", copia).returncode == 1


def test_stats_reprova_sem_relatorio_de_falhas(copia):
    (copia / "raw" / "RELATORIO-FALHAS.md").unlink()
    assert rodar(copia / "tools" / "stats.py", "--raiz", copia).returncode == 1


def test_citacao_inventada_reprova(copia):
    regras = copia / "regras.md"
    regras.write_text(regras.read_text().replace(
        '"Uma peça de cada vez"', '"Frase que a pessoa nunca disse"'))
    r = rodar(copia / "tools" / "validar_citacoes.py", "--raiz", copia)
    assert r.returncode == 1 and "1 faltando" in r.stdout


def test_citacao_normalizada_passa(copia):
    regras = copia / "regras.md"
    regras.write_text(regras.read_text().replace('"Uma peça de cada vez"', '"uma PECA de cada   vez!"'))
    assert rodar(copia / "tools" / "validar_citacoes.py", "--raiz", copia).returncode == 0


def test_ativa_com_uma_fonte_reprova(copia):
    regras = copia / "regras.md"
    texto = regras.read_text().replace("## R5 — Mostre o erro\n- status: banco", "## R5 — Mostre o erro\n- status: ativa")
    regras.write_text(texto)
    r = rodar(copia / "tools" / "validar_citacoes.py", "--raiz", copia)
    assert r.returncode == 1 and "R5" in r.stdout


def test_citacao_fora_do_raw_reprova(copia):
    regras = copia / "regras.md"
    regras.write_text(regras.read_text().replace("raw/blog/post-dizer-que-funciona.md", "wiki/hot.md", 1))
    assert rodar(copia / "tools" / "validar_citacoes.py", "--raiz", copia).returncode == 1


def test_link_quebrado_reprova(copia):
    (copia / "wiki" / "temas" / "novo.md").write_text("# Novo\n\n[[pagina-que-nao-existe]]\n")
    r = rodar(copia / "tools" / "validar_links.py", "--raiz", copia)
    assert r.returncode == 1 and "link quebrado" in r.stdout


def test_fonte_faltando_na_wiki_reprova(copia):
    (copia / "wiki" / "fontes" / "posts-posts-export-2026.md").unlink()
    assert rodar(copia / "tools" / "validar_links.py", "--raiz", copia).returncode == 1


def test_resposta_exemplo_passa():
    r = rodar(TOOLS / "validar_resposta.py", EXEMPLO / "testes/respostas/2026-10-05-contar-palavras.md", "--raiz", EXEMPLO)
    assert r.returncode == 0, r.stdout


def test_resposta_sem_versao_quebrada_reprova(copia, tmp_path):
    original = (copia / "testes/respostas/2026-10-05-contar-palavras.md").read_text()
    ruim = tmp_path / "ruim.md"
    ruim.write_text(original.replace("### Versão quebrada", "### Extra"))
    r = rodar(copia / "tools" / "validar_resposta.py", ruim, "--raiz", copia)
    assert r.returncode == 1 and "Versão quebrada" in r.stdout


def test_resposta_com_regra_inexistente_reprova(copia, tmp_path):
    ruim = tmp_path / "ruim.md"
    ruim.write_text((copia / "testes/respostas/2026-10-05-contar-palavras.md").read_text() + "\nVer R99.\n")
    assert rodar(copia / "tools" / "validar_resposta.py", ruim, "--raiz", copia).returncode == 1


def test_resposta_sem_bash_no_transcript_reprova(copia, tmp_path):
    t = tmp_path / "t.jsonl"
    t.write_text(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "funciona"}]}}) + "\n")
    r = rodar(copia / "tools" / "validar_resposta.py", copia / "testes/respostas/2026-10-05-contar-palavras.md",
              "--transcript", t, "--raiz", copia)
    assert r.returncode == 1


def test_resposta_com_bash_no_transcript_passa(copia, tmp_path):
    t = tmp_path / "t.jsonl"
    t.write_text(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "Previsão: {'a': 2}"}]}}) + "\n"
                 + json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Bash", "input": {"command": "python3 x.py"}}]}}) + "\n")
    r = rodar(copia / "tools" / "validar_resposta.py", copia / "testes/respostas/2026-10-05-contar-palavras.md",
              "--transcript", t, "--raiz", copia)
    assert r.returncode == 0, r.stdout
