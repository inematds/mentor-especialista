"""Gerador, coletores offline e o script de aceitação que deve quebrar."""
import json
import os
import subprocess
import sys

from conftest import REPO, TEMPLATE, rodar


def test_novo_mentor_gera_projeto_sem_placeholders(tmp_path):
    r = rodar(REPO / "novo-mentor.py", "teste-x", "--nome", "Fulana", "--dominio", "ensinar Y", "--destino", tmp_path)
    assert r.returncode == 0, r.stderr
    alvo = tmp_path / "mentor-teste-x"
    assert (alvo / ".claude/agents/teste-x-mentor.md").exists()
    for s in ("coletar", "compilar", "regras", "ensina", "revisa", "ingere"):
        assert (alvo / f".claude/skills/teste-x-{s}/SKILL.md").exists()
    sobras = [p for p in alvo.rglob("*") if p.is_file() and "{{" in p.read_text(encoding="utf-8", errors="ignore")]
    assert not sobras, sobras
    assert "{{" not in "".join(str(p) for p in alvo.rglob("*"))
    cfg = json.loads((alvo / "mentor.config.json").read_text())
    assert cfg["slug"] == "teste-x"
    settings = json.loads((alvo / ".claude/settings.json").read_text())
    assert {"PostToolUse", "Stop", "SubagentStop"} <= set(settings["hooks"])


def test_novo_mentor_recusa_slug_ruim_e_pasta_existente(tmp_path):
    assert rodar(REPO / "novo-mentor.py", "Slug Ruim", "--nome", "x", "--dominio", "y", "--destino", tmp_path).returncode == 2
    rodar(REPO / "novo-mentor.py", "ok", "--nome", "x", "--dominio", "y", "--destino", tmp_path)
    assert rodar(REPO / "novo-mentor.py", "ok", "--nome", "x", "--dominio", "y", "--destino", tmp_path).returncode == 1


def test_frontmatter_das_skills_e_do_agente(tmp_path):
    rodar(REPO / "novo-mentor.py", "fm", "--nome", "x", "--dominio", "y", "--destino", tmp_path)
    for md in (tmp_path / "mentor-fm/.claude").rglob("*.md"):
        linhas = md.read_text().splitlines()
        assert linhas[0] == "---", md
        cab = "\n".join(linhas[1:linhas.index("---", 1)])
        assert "name: fm-" in cab and "description:" in cab, md


def test_coletar_arquivo_registra_no_manifesto(tmp_path):
    rodar(REPO / "novo-mentor.py", "col", "--nome", "x", "--dominio", "y", "--destino", tmp_path)
    alvo = tmp_path / "mentor-col"
    fonte = tmp_path / "notas.txt"
    fonte.write_text("uma duas três quatro")
    assert rodar(alvo / "tools/coletar_arquivo.py", fonte, "--tipo", "notas", "--raiz", alvo).returncode == 0
    m = json.loads((alvo / "raw/MANIFESTO.json").read_text())
    assert m[0]["palavras"] == 4 and len(m[0]["sha256"]) == 64
    binario = tmp_path / "foto.png"
    binario.write_bytes(b"\x89PNG")
    assert rodar(alvo / "tools/coletar_arquivo.py", binario, "--tipo", "notas", "--raiz", alvo).returncode == 1
    assert "foto.png" in (alvo / "raw/RELATORIO-FALHAS.md").read_text()


def test_legenda_vtt_vira_texto_com_tempo():
    sys.path.insert(0, str(TEMPLATE / "tools"))
    from coletar_video import legenda_para_texto
    vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nolá <c>mundo</c>\n\n00:01:05.000 --> 00:01:07.000\nolá mundo\n\n01:02:03.000 --> 01:02:04.000\nfim\n"
    assert legenda_para_texto(vtt) == "[00:00:01] olá mundo\n[01:02:03] fim\n"


def test_extrator_web_ignora_script_e_nav():
    sys.path.insert(0, str(TEMPLATE / "tools"))
    from coletar_web import Extrator
    ex = Extrator()
    ex.feed("<html><title>T</title><nav>menu</nav><script>x=1</script><h2>Sub</h2><p>texto útil</p></html>")
    t = ex.texto()
    assert ex.titulo == "T" and "## Sub" in t and "texto útil" in t and "menu" not in t and "x=1" not in t


def test_script_de_aceitacao_quebra_sem_utf8_e_roda_com_utf8():
    script = TEMPLATE / "testes/aceitacao/script_emoji.py"
    ok = subprocess.run([sys.executable, str(script)], capture_output=True, text=True,
                        env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    assert ok.returncode == 0 and "3 perguntas" in ok.stdout
    ruim = subprocess.run([sys.executable, str(script)], capture_output=True, text=True,
                          env={**os.environ, "PYTHONIOENCODING": "cp1252"}, errors="replace")
    assert ruim.returncode != 0 and "UnicodeEncodeError" in ruim.stderr
    (script.parent / "relatorio.txt").unlink(missing_ok=True)


def test_exemplo_em_dia_com_template():
    """O exemplo foi gerado do template: tools e hook não podem divergir."""
    exemplo = REPO / "exemplo"
    for rel in ["tools/_comum.py", "tools/stats.py", "tools/validar_links.py", "tools/validar_citacoes.py",
                "tools/validar_resposta.py", "tools/coletar_web.py", "tools/coletar_video.py",
                "tools/coletar_repo.py", "tools/coletar_arquivo.py", ".claude/hooks/portao-execucao.py",
                ".claude/settings.json"]:
        assert (TEMPLATE / rel).read_text() == (exemplo / rel).read_text(), rel
