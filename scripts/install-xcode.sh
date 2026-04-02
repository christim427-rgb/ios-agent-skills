#!/usr/bin/env bash
# install-xcode.sh — Link agent skills into Xcode 26 agentic coding directories.
#
# Xcode 26.3 introduced native Claude Agent and Codex support. Both agents
# read skills from specific Library paths. This script symlinks skill directories
# so that updates to skills are automatically reflected in Xcode without
# re-running the script.
#
# Usage (run from the root of your iOS project after installing skills):
#   bash .github/skills/install-xcode.sh
#
# Or from this repo root to link all skills globally:
#   bash scripts/install-xcode.sh [skills-root]
#
# Arguments:
#   skills-root  Path containing skill directories (default: auto-detected)

set -euo pipefail

CLAUDE_DIR="$HOME/Library/Developer/Xcode/CodingAssistant/ClaudeAgentConfig/skills"
CODEX_DIR="$HOME/Library/Developer/Xcode/CodingAssistant/codex/skills"

# Auto-detect skills root: prefer .github/skills, fall back to skills/ios
detect_skills_root() {
  local candidates=(
    ".github/skills"
    "skills/ios"
  )
  for candidate in "${candidates[@]}"; do
    if ls "$candidate"/*/SKILL.md &>/dev/null 2>&1; then
      echo "$candidate"
      return
    fi
  done
  echo ""
}

SKILLS_ROOT="${1:-$(detect_skills_root)}"

if [[ -z "$SKILLS_ROOT" ]]; then
  echo "❌ No skills found. Install skills first:"
  echo "   npx skills add git@git.epam.com:epm-ease/research/agent-skills.git --skill '*'"
  exit 1
fi

SKILLS_ROOT="$(cd "$SKILLS_ROOT" && pwd)"
echo "📂 Skills root: $SKILLS_ROOT"

# Create target directories
mkdir -p "$CLAUDE_DIR"
mkdir -p "$CODEX_DIR"

linked=0
skipped=0

for skill_dir in "$SKILLS_ROOT"/*/; do
  [[ -f "$skill_dir/SKILL.md" ]] || continue
  skill_name="$(basename "$skill_dir")"

  for target_dir in "$CLAUDE_DIR" "$CODEX_DIR"; do
    target="$target_dir/$skill_name"
    if [[ -L "$target" ]]; then
      echo "  ↩️  Already linked: $skill_name → $target_dir"
      ((skipped++)) || true
    elif [[ -e "$target" ]]; then
      echo "  ⚠️  Skipped (not a symlink): $target"
      ((skipped++)) || true
    else
      ln -s "$skill_dir" "$target"
      echo "  ✅ Linked: $skill_name → $target_dir"
      ((linked++)) || true
    fi
  done
done

echo ""
echo "Done. Linked: $linked, Skipped: $skipped"
echo ""
echo "Restart Xcode to pick up new skills."
echo "Skills will auto-update — symlinks always point to the current files."
