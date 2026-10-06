"""Tests for hooks/guard.py: feed it the JSON Claude Code sends, check the exit code."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

GUARD = Path(__file__).resolve().parent.parent / "hooks" / "guard.py"


def run(command: str, tool: str = "Bash") -> int:
    payload = json.dumps({"tool_name": tool, "tool_input": {"command": command}})
    return subprocess.run([sys.executable, str(GUARD)], input=payload, text=True, capture_output=True).returncode


@pytest.mark.parametrize("cmd", [
    "git add -A",
    "git add .",
    "git add --all",
    "git -C repo add .",
    'git -C "my repo" add -A && git commit -m wip',
    "git commit -a -m wip",
    "git commit -am wip",
    "cd x; git add . ; git status",
])
def test_blocks_blanket_staging(cmd):
    assert run(cmd) == 2


@pytest.mark.parametrize("cmd", ["git add -A", "git commit -am wip"])
def test_blocks_in_powershell_too(cmd):
    assert run(cmd, tool="PowerShell") == 2


@pytest.mark.parametrize("cmd", [
    "git add src/app.py tests/test_app.py",
    "git add .gitignore",
    'git commit -m "fix: handle -a flag in parser"',
    "git commit --amend --no-edit",
    "git status -sb",
    "ls -A",
])
def test_allows_explicit_paths(cmd):
    assert run(cmd) == 0


def test_blocks_long_python_heredoc():
    body = "\n".join(f"print({i})" for i in range(31))
    assert run(f"python - <<'EOF'\n{body}\nEOF") == 2


def test_blocks_double_backslash_heredoc():
    assert run("python - <<'EOF'\nprint('C:\\\\path')\nEOF") == 2


def test_allows_short_heredoc():
    assert run("python - <<'EOF'\nprint('ok')\nEOF") == 0


def test_heredoc_rule_is_bash_only():
    body = "\n".join(f"print({i})" for i in range(31))
    assert run(f"python - <<'EOF'\n{body}\nEOF", tool="PowerShell") == 0


def test_other_tools_pass():
    assert run("git add -A", tool="Read") == 0


def test_fails_open_on_bad_input():
    result = subprocess.run([sys.executable, str(GUARD)], input="not json", text=True, capture_output=True)
    assert result.returncode == 0
