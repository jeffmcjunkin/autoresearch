#!/bin/bash
env -u ANTHROPIC_API_KEY -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT -u CLAUDE_CODE_CHILD_SESSION -u CLAUDE_CODE_SESSION_ID -u CLAUDE_CODE_EXECPATH \
  timeout 120 claude -p "Reply with exactly this token and nothing else: PLUMBING_OK" --dangerously-skip-permissions 2>&1
echo "[exit=$?]"
