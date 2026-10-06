#!/usr/bin/env bash
# Count open Dependabot alerts across every repo of a GitHub owner.
# Usage: count-alerts.sh <owner>     (needs an authenticated `gh`)
set -euo pipefail
owner="${1:?usage: count-alerts.sh <github-owner>}"

for r in $(gh repo list "$owner" --limit 200 --json name -q '.[].name'); do
  # 204 = Dependabot alerts enabled, 404 = disabled
  on=$(gh api "repos/$owner/$r/vulnerability-alerts" -i 2>/dev/null | head -1 | grep -c 204 || true)
  # --paginate matters: without it the count stops at the first page
  n=$(gh api --paginate "repos/$owner/$r/dependabot/alerts?state=open&per_page=100" -q '.[].number' 2>/dev/null | wc -l)
  echo "$r alerts_on=$on open=$n"
done
