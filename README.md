# claude-code-kit

A small set of [Claude Code](https://claude.com/claude-code) skills and a safety hook that I use every day. They are cleaned-up copies of my own setup, with personal and customer details removed.

## Why these exist

I build and run several production apps alone, with Claude Code as my main development tool. In October 2026 I reviewed **140 of my own sessions** (30 days, all projects) to find where time was lost. The same problems kept coming back:

- **Context lost between sessions.** About 100 of the 140 sessions ended with a manual "prepare to clear" handover, written differently each time.
- **Parallel sessions stepping on each other.** Several Claude sessions share one checkout. A `git add -A` in one session can commit another session's half-finished work.
- **Long inline Python scripts breaking.** Quoting and backslashes get mangled inside shell heredocs.
- **Security alerts under-counted.** Unpaginated GitHub API calls stop at the first page.

Each problem became either a **skill** (a checklist Claude loads when a phrase matches) or a **hook** (code that blocks a command before it runs).

## What's inside

| Path | What it does |
|---|---|
| `hooks/guard.py` | `PreToolUse` hook for Bash/PowerShell. Blocks `git add -A / --all / .` and `git commit -a`, and long or double-backslash Python heredocs. Fails open on input it can't parse. |
| `tests/test_guard.py` | 22 pytest cases: what must be blocked, what must pass (e.g. `git add .gitignore`, `git commit --amend`). Run in CI on every push. |
| `skills/prepare-to-clear/` | End-of-session wrap-up: stop your own processes, commit by explicit path, push every remote, check deploys, update memory, write a handover with decisions quoted verbatim. Also a resume mode. |
| `skills/security-sweep/` | Weekly Dependabot sweep across all repos: paginated count, triage by reachability, safe upgrade commands for uv and npm, deploy, then re-count. |

## Install

```bash
# skills (user level)
cp -r skills/* ~/.claude/skills/

# hook
mkdir -p ~/.claude/hooks && cp hooks/guard.py ~/.claude/hooks/
```

Then add the hook to `~/.claude/settings.json` (see `settings.example.json`):

```json
"hooks": {
  "PreToolUse": [
    { "matcher": "Bash|PowerShell",
      "hooks": [{ "type": "command", "command": "python ~/.claude/hooks/guard.py", "timeout": 10 }] }
  ]
}
```

On Windows, use the full path to `guard.py` in `command`.

## Tests

```bash
pip install pytest
pytest -q
```

## Licence

MIT
