---
name: prepare-to-clear
description: End-of-session wrap-up so the user can safely run /clear. Load when the user says "prepare to clear", "prepare for clear", "ready to clear?", "handover", "summarize, we need to clear", "write what we've done" — and in resume mode for "resume", "pick up <doc>", "continue from last session". Never ask what the phrase means.
---

# Prepare to clear

"Prepare to clear" = make this session safe to wipe. **The user types `/clear` afterwards** — don't ask what it means, don't hand steps back. Run the whole checklist; only stop for a real decision.

## 1. Stop what this session started
- Stop your own background shells, monitors, ssh tunnels and dev servers. Leave other sessions' and the user's processes alone.
- Anything deliberately left running (e.g. a local simulator on a port) goes in the final message.

## 2. Git (in a repo)
- `git status -sb` + `git log @{u}.. --oneline`. Other sessions may have edited files since you started — only commit what YOU changed.
- Stage by explicit path. **Never** `git add -A`, `git add .`, `git commit -a` (parallel sessions share checkouts; `hooks/guard.py` enforces this).
- Push every remote in `git remote -v`, not just `origin`.
- If production should run HEAD (the repo's CLAUDE.md says so): deploy with the repo's deploy script and check that the deployed sha = HEAD.
- Open staged roll-out (canary)? State plainly whether it still needs to be widened to the rest of the fleet.

## 3. State that isn't in git
- Live edits on a server (config files, `.env`), files outside the repo, settings changes → list them in memory or the handover.

## 4. Memory + docs
- Edit the EXISTING memory file per topic (don't add a near-duplicate); retire facts that became wrong; keep its `MEMORY.md` index line to one short line. Index > ~100 lines → tighten it.
- Repo-maintained docs per the repo's CLAUDE.md (e.g. a history log with a short top entry, an open-items list).

## 5. Handover — only if work is unfinished
Update `docs/handover.md` (repo) or the topic's memory file with:
- The user's decisions, **quoted verbatim**
- Shipped commit SHAs
- Dead ends (what failed, why)
- Open questions as numbered options + your default
- A 3-line resume prompt

## 6. Final message (≤12 lines, nothing else)
```
✅ READY TO /clear   (or ⛔ NOT READY — <blocker>)
- Git: <sha> pushed to <remotes> | nothing to commit
- Deployed: <yes @sha | no | n/a>
- Left running: <…|nothing>
- Updated: <memory/doc files>
- Waiting on you: 1) … 2) …
- Metered API spend this session: <$x | none>
```

## Resume mode
- Read the handover + related memory, then `git log --oneline` since it was written.
- Restate the user's last decisions in 3 bullets **before** acting ("you forgot everything" is the failure to avoid).
