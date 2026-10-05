"""Regressões do piloto real (kit 1.2): cada teste corresponde a uma linha do diário do piloto."""
import json
import os
import shutil
import subprocess
import sys

from conftest import EXEMPLO, REPO, TEMPLATE, rodar


def novo(tmp_path, slug="p"):
    r = rodar(REPO / "novo-mentor.py", slug, "--nome", "x", "--dominio", "y", "--destino", tmp_path)
    assert r.returncode == 0, r.stderr
    return tmp_path / f"mentor-{slug}"


def test_manifesto_nao_perde_itens_com_coleta_em_paralelo(tmp_path):
    alvo = novo(tmp_path)
    fontes = []
    for i in range(12):
        f = tmp_path / f"f{i}.txt"
        f.write_text(f"texto {i} " * 50)
        fontes.append(f)
    procs = [subprocess.Popen([sys.executable, str(alvo / "tools/coletar_arquivo.py"), str(f), "--tipo", "notas",
                               "--raiz", str(alvo)], stdout=subprocess.DEVNULL) for f in fontes]
    assert all(p.wait() == 0 for p in procs)
    assert len(json.loads((alvo / "raw/MANIFESTO.json").read_text())) == 12


def test_transcricoes_com_mesmo_nome_nao_se_sobrescrevem(tmp_path):
    alvo = novo(tmp_path)
    cfg = json.loads((alvo / "mentor.config.json").read_text())
    cfg["transcrever_cmd"] = "echo fala do video {url} > {saida}/transcript.txt"
    (alvo / "mentor.config.json").write_text(json.dumps(cfg))
    sem_ytdlp = {**os.environ, "PATH": "/usr/bin:/bin"}  # força o caminho do transcritor
    if shutil.which("yt-dlp", path=sem_ytdlp["PATH"]):
        import pytest
        pytest.skip("yt-dlp em /usr/bin")
    for url in ("https://ex.com/v1", "https://ex.com/v2"):
        r = subprocess.run([sys.executable, str(alvo / "tools/coletar_video.py"), url, "--raiz", str(alvo)],
                           capture_output=True, text=True, env=sem_ytdlp)
        assert r.returncode == 0, r.stdout + r.stderr
    m = json.loads((alvo / "raw/MANIFESTO.json").read_text())
    assert len(m) == 2 and len({i["arquivo"] for i in m}) == 2
    assert rodar(alvo / "tools/stats.py", "--raiz", alvo).stdout.count("video") >= 1
    for i in m:
        assert (alvo / i["arquivo"]).exists()


def test_citacao_que_cruza_marca_de_tempo_e_encontrada(tmp_path):
    alvo = novo(tmp_path)
    (alvo / "raw/videos").mkdir(parents=True)
    raw = alvo / "raw/videos/a.txt"
    raw.write_text("[00:01:00] primeiro a gente mede\n[00:01:03] antes de acreditar em qualquer coisa\n")
    (alvo / "raw/b.md").write_text("mede antes de acreditar sempre")
    (alvo / "regras.md").write_text(
        '## R1 — Medir\n- status: ativa\n- citacoes:\n'
        '  - "a gente mede antes de acreditar" — raw/videos/a.txt@00:01:00\n'
        '  - "mede antes de acreditar" — raw/b.md\n')
    r = rodar(alvo / "tools/validar_citacoes.py", "--raiz", alvo)
    assert r.returncode == 0, r.stdout


def test_stats_diz_quanto_falta(tmp_path):
    alvo = novo(tmp_path)
    f = tmp_path / "n.txt"
    f.write_text("uma duas três")
    rodar(alvo / "tools/coletar_arquivo.py", f, "--tipo", "video", "--raiz", alvo)
    (alvo / "raw/RELATORIO-FALHAS.md").write_text("x")
    r = rodar(alvo / "tools/stats.py", "--raiz", alvo)
    assert r.returncode == 1 and "faltam 4 item(ns) e 19997 palavras" in r.stdout


def _transcript(tmp_path, eventos):
    t = tmp_path / "t.jsonl"
    linhas = []
    for k, v in eventos:
        c = {"type": "text", "text": v} if k == "T" else {"type": "tool_use", "name": "Bash", "input": {"command": v}}
        linhas.append(json.dumps({"type": "assistant", "message": {"content": [c]}}))
    t.write_text("\n".join(linhas) + "\n")
    return t


def test_previsao_depois_de_rodar_reprova(tmp_path):
    t = _transcript(tmp_path, [("B", "cat x.py"), ("B", "python3 x.py"), ("T", "Previsão: vai dar 3")])
    r = rodar(EXEMPLO / "tools/validar_resposta.py", EXEMPLO / "testes/respostas/2026-10-05-contar-palavras.md",
              "--transcript", t, "--raiz", EXEMPLO)
    assert r.returncode == 1 and "ANTES de qualquer previsão" in r.stdout


def test_previsao_antes_de_rodar_passa(tmp_path):
    t = _transcript(tmp_path, [("B", "cat x.py && ls"), ("T", "Previsão: vai dar 3"), ("B", "python3 x.py")])
    r = rodar(EXEMPLO / "tools/validar_resposta.py", EXEMPLO / "testes/respostas/2026-10-05-contar-palavras.md",
              "--transcript", t, "--raiz", EXEMPLO)
    assert r.returncode == 0, r.stdout


def test_perfil_revisao_exige_secoes_de_revisao(tmp_path):
    rev = tmp_path / "rev.md"
    rev.write_text("## Previsão\nquebra em cp1252 (R3)\n## Reprodução\nx\n## Correção\nx\n## Lado a lado\nx\n## Relatório\nR4\n")
    assert rodar(EXEMPLO / "tools/validar_resposta.py", rev, "--perfil", "revisao", "--raiz", EXEMPLO).returncode == 0
    rev.write_text("## Reprodução\nx\n## Relatório\nR4\n")
    r = rodar(EXEMPLO / "tools/validar_resposta.py", rev, "--perfil", "revisao", "--raiz", EXEMPLO)
    assert r.returncode == 1 and "Previsão" in r.stdout


def test_secoes_do_especialista_no_config_sao_cobradas(tmp_path):
    copia = tmp_path / "m"
    shutil.copytree(EXEMPLO, copia)
    cfg = json.loads((copia / "mentor.config.json").read_text())
    cfg["secoes_resposta"] = cfg["secoes_resposta"] + ["Sua vez"]
    (copia / "mentor.config.json").write_text(json.dumps(cfg))
    r = rodar(copia / "tools/validar_resposta.py", copia / "testes/respostas/2026-10-05-contar-palavras.md", "--raiz", copia)
    assert r.returncode == 1 and "Sua vez" in r.stdout


def test_atualizar_preserva_conteudo_e_traz_kit_novo(tmp_path):
    alvo = novo(tmp_path, "upd")
    (alvo / "regras.md").write_text("## R1 — minha regra\n")
    (alvo / "ESCOPO.md").write_text("meu escopo")
    cfg = json.loads((alvo / "mentor.config.json").read_text())
    cfg["transcrever_cmd"] = "meu-transcritor"
    del cfg["secoes_revisao"]
    (alvo / "mentor.config.json").write_text(json.dumps(cfg))
    (alvo / "tools/stats.py").write_text("# versão velha\n")
    agente = alvo / ".claude/agents/upd-mentor.md"
    agente.write_text("agente personalizado")
    r = rodar(REPO / "novo-mentor.py", "--atualizar", alvo)
    assert r.returncode == 0, r.stderr
    assert (alvo / "regras.md").read_text() == "## R1 — minha regra\n"
    assert (alvo / "ESCOPO.md").read_text() == "meu escopo"
    assert (alvo / "tools/stats.py").read_text() == (TEMPLATE / "tools/stats.py").read_text()
    novo_cfg = json.loads((alvo / "mentor.config.json").read_text())
    assert novo_cfg["transcrever_cmd"] == "meu-transcritor" and "secoes_revisao" in novo_cfg
    assert "agente personalizado" in next((alvo / ".mentor").rglob("upd-mentor.md")).read_text()
    assert "name: upd-mentor" in agente.read_text()


def test_atualizar_recusa_pasta_que_nao_e_mentor(tmp_path):
    assert rodar(REPO / "novo-mentor.py", "--atualizar", tmp_path).returncode == 1


# --- casos reais dos logs do piloto ---
def _evt(k, v, **extra):
    c = {"type": "text", "text": v} if k == "T" else {"type": "tool_use", "name": "Bash", "input": {"command": v}}
    return json.dumps({"type": "assistant", "message": {"role": "assistant", "content": [c]}, **extra})


def _sessao(tmp_path, principal, subagentes=()):
    sess = "sess-1"
    tmp_path.mkdir(parents=True, exist_ok=True)
    t = tmp_path / f"{sess}.jsonl"
    t.write_text("\n".join([json.dumps({"type": "system", "session_id": sess})] + principal) + "\n")
    for i, sub in enumerate(subagentes):
        d = tmp_path / sess / "subagents"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"agent-{i}.jsonl").write_text("\n".join(sub) + "\n")
    return t


def _previu(t):
    sys.path.insert(0, str(TEMPLATE / "tools"))
    from validar_resposta import previu_antes
    return previu_antes(t)


def test_pedido_ao_subagente_com_previsao_nao_conta(tmp_path):
    pedido = json.dumps({"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": "preveja onde quebra"}]}})
    t = _sessao(tmp_path, [], [[pedido, _evt("B", "cat s.py"), _evt("B", "PYTHONIOENCODING=cp1252 python3 s.py")]])
    assert _previu(t) is False


def test_mentor_subagente_previu_e_orquestrador_confere_depois(tmp_path):
    principal = [_evt("B", "python3 tools/validar_resposta.py r.md; python3 hook.py")]
    sub = [_evt("B", 'cat a; grep -il "hook\\|portao" w/*.md | head; claude --version 2>/dev/null'),
           _evt("B", "mkdir -p out"), _evt("T", "Previsão: 2 itens abertos"), _evt("B", "python3 out/hook.py")]
    assert _previu(_sessao(tmp_path, principal, [sub])) is True


def test_sem_subagente_avalia_a_propria_sessao(tmp_path):
    assert _previu(_sessao(tmp_path, [_evt("B", "python3 x.py"), _evt("T", "Previsão: 3")])) is False
    assert _previu(_sessao(tmp_path / "b", [_evt("T", "Previsão: 3"), _evt("B", "python3 x.py")])) is True


def test_eventos_de_subagente_no_stream_principal_sao_ignorados(tmp_path):
    t = _sessao(tmp_path, [_evt("B", "python3 x.py", parent_tool_use_id="toolu_1"), _evt("T", "Previsão: 3"),
                           _evt("B", "python3 x.py")])
    assert _previu(t) is True


def test_comando_negado_pelo_portao_nao_conta_como_execucao(tmp_path):
    neg = json.dumps({"type": "user", "message": {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": "t1", "is_error": True,
         "content": "PreToolUse:Bash hook error: Portão de previsão: antes de executar código, escreva…"}]}})
    tu = json.dumps({"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "python3 s.py"}}]}})
    sub = [tu, neg, _evt("T", "Previsão: UnicodeEncodeError"), _evt("B", "python3 s.py")]
    assert _previu(_sessao(tmp_path, [], [sub])) is True
