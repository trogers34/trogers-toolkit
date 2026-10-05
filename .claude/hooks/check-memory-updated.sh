#!/usr/bin/env bash
# After a git commit, check that any commit touching the Church History site also
# updated its project memory (church-history/CLAUDE.md). If not, tell Claude to do it.
cd "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}" || exit 0
files=$(git show --name-only --pretty=format: HEAD 2>/dev/null) || exit 0
if grep -q '^church-history/' <<<"$files" && ! grep -qx 'church-history/CLAUDE.md' <<<"$files"; then
  msg="The last commit changed church-history/ but did not update the project memory. Update church-history/CLAUDE.md (people list, rules, and the change log) to reflect this commit, then commit it."
  jq -n --arg m "$msg" '{systemMessage: $m, hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $m}}'
fi
exit 0
