import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
TEMPLATE = REPO / "template"
EXEMPLO = REPO / "exemplo"
HOOK = TEMPLATE / ".claude" / "hooks" / "portao-execucao.py"


def rodar(script: Path, *args, cwd=None):
    return subprocess.run([sys.executable, str(script), *map(str, args)], capture_output=True, text=True, cwd=cwd)


@pytest.fixture
def hook(tmp_path):
    """Chama o portão como o Claude Code chama: JSON no stdin."""
    def chamar(evento: dict):
        evento = {"session_id": "teste", "cwd": str(tmp_path), **evento}
        env = {**os.environ, "CLAUDE_PROJECT_DIR": str(tmp_path)}
        r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(evento), capture_output=True, text=True, env=env)
        assert r.returncode == 0, r.stderr
        return json.loads(r.stdout) if r.stdout.strip() else None
    chamar.raiz = tmp_path
    return chamar
