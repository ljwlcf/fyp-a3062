#!/bin/bash
# Stop hook: a session that changed anything may not end until the notes are
# updated, everything is committed, and the commits are pushed.
# Exit 2 = block the stop and show stderr to Claude so it fixes the gap.
input=$(cat)
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

# Avoid an endless loop: if we already blocked once and Claude still can't
# comply (e.g. no network for push), let it stop but say so loudly.
if echo "$input" | grep -q '"stop_hook_active"[[:space:]]*:[[:space:]]*true'; then
  soft=1
fi

start_sha=$(cat .claude/state/session-start-sha 2>/dev/null)
marker=.claude/state/session-start-time
problems=()

dirty=$(git status --porcelain 2>/dev/null)
head_sha=$(git rev-parse HEAD 2>/dev/null)

# Nothing happened this session (Q&A only): allow the stop.
if [ -z "$dirty" ] && [ -n "$start_sha" ] && [ "$head_sha" = "$start_sha" ] \
   && [ -z "$(find ablation/results -newer "$marker" -type f 2>/dev/null | head -1)" ]; then
  exit 0
fi

changed_since_start() {  # committed or uncommitted change to $1 since session start
  { [ -n "$start_sha" ] && git diff --name-only "$start_sha" -- "$1" 2>/dev/null; \
    git status --porcelain -- "$1" 2>/dev/null; } | grep -q .
}

changed_since_start notes/progress.md || \
  problems+=("notes/progress.md has no new entry. Add a Did / Broke / Next entry at the top for $(date +%Y-%m-%d).")

if [ -n "$(find ablation/results -newer "$marker" -type f 2>/dev/null | head -1)" ]; then
  changed_since_start notes/results.md || \
    problems+=("New files in ablation/results/ but notes/results.md was not updated. Add an entry naming the config.")
fi

[ -n "$(git status --porcelain 2>/dev/null)" ] && \
  problems+=("Uncommitted changes. Commit them with a clear message.")

upstream=$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null)
if [ -n "$upstream" ]; then
  ahead=$(git rev-list --count "$upstream"..HEAD 2>/dev/null)
  [ "${ahead:-0}" -gt 0 ] && problems+=("$ahead commit(s) not pushed. Run git push so chat sees the current state.")
fi

[ ${#problems[@]} -eq 0 ] && exit 0

{
  echo "Session hand-off incomplete (see CLAUDE.md, 'Hand-off between Claude Code and chat'):"
  for p in "${problems[@]}"; do echo "- $p"; done
  echo "Also: log any decision in notes/decisions.md and park any non-code question in notes/for-chat.md."
} >&2

if [ -n "$soft" ]; then
  echo "WARNING: stopping with the hand-off still incomplete. Tell the user what is missing." >&2
  exit 0
fi
exit 2
