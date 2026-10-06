"""PreToolUse guard for Bash/PowerShell (user-level, all projects).

Blocks (exit 2 + reason on stderr):
  1. Blanket staging/committing: `git add -A|--all|.`, `git commit -a/-am` —
     parallel Claude sessions share checkouts, so only stage explicit paths.
  2. Long or double-backslash Python heredocs (`python - <<EOF` …) — they keep
     breaking on quoting/escapes; write a .py file with the Write tool instead.
Anything unparseable is allowed (fail open).
"""
import json
import re
import sys

GIT = r"\bgit\b(?:\s+-C\s+(?:\"[^\"]*\"|'[^']*'|\S+))*\s+"
ADD_ALL = re.compile(GIT + r"add\b[^\n;&|]*?\s(?:-A|--all|\.)(?=\s|$|[;&|])")
COMMIT_ALL = re.compile(GIT + r"commit\b[^\n;&|\"']*?\s-(?!-)[a-zA-Z]*a[a-zA-Z]*(?=\s|$)")
PY_HEREDOC = re.compile(r"\bpython[0-9.]*(?:\.exe)?\s+(?:-\s+)?<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n(.*?)\n\1\b", re.S)


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("tool_name") not in ("Bash", "PowerShell"):
        return 0
    cmd = str((data.get("tool_input") or {}).get("command", ""))
    if ADD_ALL.search(cmd) or COMMIT_ALL.search(cmd):
        print("Blocked by ~/.claude/hooks/guard.py: don't use `git add -A/--all/.` or `git commit -a` — "
              "other Claude sessions share this checkout. Stage the files you changed by explicit path.",
              file=sys.stderr)
        return 2
    if data.get("tool_name") == "Bash":
        for m in PY_HEREDOC.finditer(cmd):
            body = m.group(2)
            if body.count("\n") + 1 > 30 or "\\\\" in body:
                print("Blocked by ~/.claude/hooks/guard.py: long or double-backslash Python heredocs keep breaking "
                      "(quoting/escapes get mangled). Write the script to a .py file with the Write tool "
                      "(scratchpad/job tmp dir), then run `python <file>`.", file=sys.stderr)
                return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
