"""Portão de previsão (kit 1.3): executar código só depois de escrever 'Previsão:' no turno."""
import json

from conftest import TEMPLATE

SETTINGS = TEMPLATE / ".claude" / "settings.json"


def linha(papel, conteudo):
    return json.dumps({"type": papel, "message": {"role": papel, "content": conteudo}})


def texto(t):
    return [{"type": "text", "text": t}]


def transcricao(pasta, nome, eventos):
    pasta.mkdir(parents=True, exist_ok=True)
    p = pasta / nome
    p.write_text("\n".join(eventos) + "\n")
    return p


def pre(hook, cmd, tp, **extra):
    return hook({"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": cmd},
                 "transcript_path": str(tp), **extra})


def negado(r):
    return r and r["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_registrado_no_settings():
    assert "PreToolUse" in json.loads(SETTINGS.read_text())["hooks"]


def test_executar_sem_previsao_e_negado(hook):
    tp = transcricao(hook.raiz, "s.jsonl", [linha("user", "revise o script"), linha("assistant", texto("vou rodar"))])
    r = pre(hook, "PYTHONIOENCODING=cp1252 python3 script.py", tp)
    assert negado(r) and "Previsão" in r["hookSpecificOutput"]["permissionDecisionReason"]


def test_com_previsao_no_turno_passa(hook):
    tp = transcricao(hook.raiz, "s.jsonl", [linha("user", "revise"), linha("assistant", texto("Previsão: UnicodeEncodeError no 🔎"))])
    assert pre(hook, "python3 script.py", tp) is None


def test_previsao_de_turno_anterior_nao_vale(hook):
    tp = transcricao(hook.raiz, "s.jsonl", [linha("user", "a"), linha("assistant", texto("Previsão: 3")),
                                            linha("user", "agora outra coisa")])
    assert negado(pre(hook, "python3 x.py", tp))


def test_resultado_de_ferramenta_nao_comeca_turno_novo(hook):
    tp = transcricao(hook.raiz, "s.jsonl", [linha("user", "a"), linha("assistant", texto("Previsão: 3")),
                                            linha("user", [{"type": "tool_result", "content": "ok"}])])
    assert pre(hook, "python3 x.py", tp) is None


def test_ler_listar_kit_e_versao_passam_sem_previsao(hook):
    tp = transcricao(hook.raiz, "s.jsonl", [linha("user", "a")])
    for cmd in ["cat x.py", "ls -la; grep -n foo x.py", "git status", "python3 tools/validar_resposta.py r.md",
                "claude --version", "python3 --version", 'grep "a\\|b" x.py | head']:
        assert pre(hook, cmd, tp) is None, cmd


def test_subagente_usa_a_propria_transcricao(hook):
    principal = transcricao(hook.raiz, "sess.jsonl", [linha("user", "a"), linha("assistant", texto("Previsão: nada"))])
    transcricao(hook.raiz / "sess" / "subagents", "agent-abc.jsonl", [linha("user", "revise"), linha("assistant", texto("lendo"))])
    assert negado(pre(hook, "python3 x.py", principal, agent_id="abc", session_id="sess"))
    transcricao(hook.raiz / "sess" / "subagents", "agent-abc.jsonl",
                [linha("user", "revise"), linha("assistant", texto("Previsão: quebra"))])
    assert pre(hook, "python3 x.py", principal, agent_id="abc", session_id="sess") is None


def test_sem_transcricao_deixa_passar(hook):
    assert pre(hook, "python3 x.py", hook.raiz / "nao-existe.jsonl") is None


def test_desligavel_no_config(hook):
    (hook.raiz / "mentor.config.json").write_text(json.dumps({"portao": {"previsao": False}}))
    tp = transcricao(hook.raiz, "s.jsonl", [linha("user", "a")])
    assert pre(hook, "python3 x.py", tp) is None
