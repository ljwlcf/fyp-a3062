#!/bin/bash
# SessionStart hook: record where this session began, and load the hand-off state
# into Claude's context so every session starts from the notes, not from memory.
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
mkdir -p .claude/state
git rev-parse HEAD > .claude/state/session-start-sha 2>/dev/null
touch .claude/state/session-start-time

git pull --ff-only --quiet 2>/dev/null || echo "NOTE: git pull failed or needs a merge; check before working."

echo "=== Hand-off state (from notes/) ==="
echo
echo "--- Latest progress entry ---"
awk '/^## [0-9]{4}-[0-9]{2}-[0-9]{2}/{n++} n==1' notes/progress.md 2>/dev/null | head -25
echo
echo "--- notes/for-chat.md ---"
cat notes/for-chat.md 2>/dev/null
echo
echo "Before starting: apply anything new under 'Answered' in for-chat.md and in decisions.md."
echo "Park any non-code question (scope, direction, supervisor, report framing) in for-chat.md."
exit 0
