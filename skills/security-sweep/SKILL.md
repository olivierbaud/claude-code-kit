---
name: security-sweep
description: Sweep all of the owner's GitHub repos for open Dependabot/security alerts, fix them, deploy and re-count. Load for "security sweep", "check dependabot", "any CVEs", "vulnerability alerts", "are my repos secure", or a scheduled weekly run.
---

# Security sweep

Keep a dated audit log (e.g. a `security_audits.md` memory file). Read it first; append to it last.

## 1. Count — paginate, or the numbers lie
Run `scripts/count-alerts.sh <github-owner>`. It lists every repo with `alerts_on` (Dependabot alerts enabled) and the number of open alerts.

Without `--paginate` the GitHub API under-counts: a manual check once found 61 open alerts when the unpaginated count said far fewer. Keep the loop in the script file — long inline shell loops break on quoting.

## 2. Triage per alert
- Use each alert's `security_advisory.severity` and `security_vulnerability.first_patched_version` — **don't trust a Dependabot PR to target the patched version** (it can be stale).
- Is the vulnerable code path reachable? Say so in one line (e.g. "next/og RCE — no next/og import").

## 3. Fix
- Python/uv: `uv lock --upgrade-package <name>` — **never** a blind `uv lock --upgrade` (it pulls major versions of unrelated SDKs).
- npm: pinned exact versions ignore `npm audit fix` → `npm install <pkg>@<patched>`; nested deps → `overrides` (delete stale nested lock entries if npm ignores the override). Also run `npm audit` — it finds clusters Dependabot never filed.
- Run the repo's tests; commit by explicit path; PR or push per the repo's habit.

## 4. Deploy + re-count
- Deploy every affected service (all checkouts / environments, not just one).
- Re-run step 1. Turning alerts on doesn't fix anything — re-check the counts.
- New repo found with alerts off → `gh api -X PUT repos/<owner>/<repo>/vulnerability-alerts` and `.../automated-security-fixes`. Leave version updates OFF (noise).

## 5. Record
Append a dated line to the audit log: repos swept, alerts fixed, commits, what's left.

## Output
Verdict first ("3 repos had 7 alerts → all fixed & deployed" / "2 left, why"), then a table: repo · open before · fixed · deployed · open after.
