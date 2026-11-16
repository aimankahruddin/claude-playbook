#!/usr/bin/env bash
# Copy the playbook skills and the advisor agent into ~/.claude (or $CLAUDE_CONFIG_DIR).
# Existing copies are moved to backups/opus-playbook-<time>/ rather than overwritten.
set -euo pipefail
src="$(cd "$(dirname "$0")" && pwd)"
dest="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
bak="$dest/backups/opus-playbook-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$dest/skills" "$dest/agents"
for dir in "$src"/skills/*/; do
  name="$(basename "$dir")"
  if [ -e "$dest/skills/$name" ]; then
    mkdir -p "$bak/skills" && mv "$dest/skills/$name" "$bak/skills/$name"
  fi
  cp -R "$dir" "$dest/skills/$name"
  echo "installed skill: $name"
done
agent="$dest/agents/fable-advisor.md"
if [ -e "$agent" ]; then
  mkdir -p "$bak/agents" && mv "$agent" "$bak/agents/"
fi
cp "$src/agents/fable-advisor.md" "$agent"
echo "installed agent: fable-advisor"
echo "Done. Open a new Claude Code session and run /audit-setup"
