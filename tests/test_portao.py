"""Portão de execução: os 5 casos do plano + armadilhas."""


def editar(hook, nome):
    return hook({"hook_event_name": "PostToolUse", "tool_name": "Write", "tool_input": {"file_path": str(hook.raiz / nome)}})


def bash(hook, cmd):
    return hook({"hook_event_name": "PostToolUse", "tool_name": "Bash", "tool_input": {"command": cmd}})


def parar(hook, evento="Stop", ativo=False):
    return hook({"hook_event_name": evento, "stop_hook_active": ativo})


def test_1_editou_e_rodou_passa(hook):
    editar(hook, "calc.py")
    bash(hook, "python3 calc.py --x 2")
    assert parar(hook) is None


def test_2_editou_e_nao_rodou_bloqueia(hook):
    editar(hook, "calc.py")
    r = parar(hook)
    assert r["decision"] == "block" and "calc.py" in r["reason"]


def test_3_so_markdown_passa(hook):
    editar(hook, "NOTAS.md")
    assert parar(hook) is None


def test_4_stop_hook_active_passa(hook):
    editar(hook, "calc.py")
    assert parar(hook, ativo=True) is None


def test_5_subagentstop_tambem_bloqueia(hook):
    editar(hook, "calc.py")
    assert parar(hook, evento="SubagentStop")["decision"] == "block"


def test_ls_e_cat_nao_contam_como_execucao(hook):
    editar(hook, "calc.py")
    bash(hook, "ls -la")
    bash(hook, "cat calc.py")
    assert parar(hook)["decision"] == "block"


def test_pytest_limpa_arquivos_python(hook):
    editar(hook, "calc.py")
    bash(hook, "python3 -m pytest -q")
    assert parar(hook) is None


def test_modulo_com_dash_m(hook):
    editar(hook, "pacote/tokenizador.py")
    bash(hook, "python3 -m pacote.tokenizador")
    assert parar(hook) is None


def test_arquivo_em_raw_e_ignorado(hook):
    editar(hook, "raw/repos/algo.py")
    assert parar(hook) is None


def test_so_limpa_o_arquivo_executado(hook):
    editar(hook, "a.py")
    editar(hook, "b.sh")
    bash(hook, "bash b.sh")
    r = parar(hook)
    assert "a.py" in r["reason"] and "b.sh" not in r["reason"]


def test_sessoes_separadas(hook):
    editar(hook, "calc.py")
    r = hook({"hook_event_name": "Stop", "session_id": "outra"})
    assert r is None


def test_entrada_invalida_nao_derruba(hook):
    import subprocess
    import sys
    from conftest import HOOK
    r = subprocess.run([sys.executable, str(HOOK)], input="isto não é json", capture_output=True, text=True)
    assert r.returncode == 0


# --- regressões apontadas na verificação 1.0.0 ---
import pytest  # noqa: E402


@pytest.mark.parametrize("cmd", [
    'git commit -m "fix calc.py"', "rm calc.py", "chmod +x calc.py", "ruff check calc.py",
    "python3 -m py_compile calc.py", 'echo "calc.py" > log.txt', "cd . && cat calc.py",
    "pip install pytest", "git add calc.py", "cat calc.py | python3",
])
def test_comandos_que_nao_executam(hook, cmd):
    editar(hook, "calc.py")
    bash(hook, cmd)
    assert parar(hook)["decision"] == "block", cmd


def test_bash_n_nao_executa(hook):
    editar(hook, "x.sh")
    bash(hook, "bash -n x.sh")
    assert parar(hook)["decision"] == "block"


def test_mesmo_nome_em_pastas_diferentes(hook):
    editar(hook, "a/calc.py")
    editar(hook, "b/calc.py")
    bash(hook, "python3 a/calc.py")
    r = parar(hook)
    assert r and r["reason"].count("calc.py") == 1


def test_cd_e_depois_roda(hook):
    editar(hook, "tools/calc.py")
    bash(hook, "cd tools && python3 calc.py")
    assert parar(hook) is None


def test_npm_test_limpa_tsx(hook):
    editar(hook, "src/App.tsx")
    bash(hook, "npm test")
    assert parar(hook) is None


def test_variavel_de_ambiente_antes(hook):
    editar(hook, "calc.py")
    bash(hook, "PYTHONIOENCODING=cp1252 python3 calc.py")
    assert parar(hook) is None


def test_avisado_nao_bloqueia_de_novo_ate_reeditar(hook):
    editar(hook, "calc.py")
    assert parar(hook)["decision"] == "block"
    assert parar(hook, ativo=True) is None
    assert parar(hook) is None  # turno seguinte: já avisado
    editar(hook, "calc.py")
    assert parar(hook)["decision"] == "block"  # reeditou → volta a cobrar
