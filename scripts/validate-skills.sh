#!/bin/bash
# Validates all skills in the repository
set -e

ERRORS=0

for skill_dir in skills/*/*/; do
  skill_name=$(basename "$skill_dir")

  # Skip any non-skill directories (workspaces are no longer inside skills/)

  # Check SKILL.md exists
  if [[ ! -f "$skill_dir/SKILL.md" ]]; then
    echo "❌ $skill_name: Missing SKILL.md"
    ERRORS=$((ERRORS + 1))
    continue
  fi

  # Check YAML frontmatter
  if ! head -1 "$skill_dir/SKILL.md" | grep -q "^---"; then
    echo "❌ $skill_name: SKILL.md missing YAML frontmatter"
    ERRORS=$((ERRORS + 1))
  fi

  # Check name field in frontmatter
  if ! grep -q "^name:" "$skill_dir/SKILL.md"; then
    echo "❌ $skill_name: SKILL.md missing 'name' in frontmatter"
    ERRORS=$((ERRORS + 1))
  fi

  # Check description field
  if ! grep -q "^description:" "$skill_dir/SKILL.md"; then
    echo "❌ $skill_name: SKILL.md missing 'description' in frontmatter"
    ERRORS=$((ERRORS + 1))
  fi

  # Check skill name matches directory name
  yaml_name=$(grep "^name:" "$skill_dir/SKILL.md" | head -1 | sed 's/name: *//')
  if [[ "$yaml_name" != "$skill_name" ]]; then
    echo "⚠️  $skill_name: YAML name '$yaml_name' ≠ directory name '$skill_name'"
  fi

  # Check marketplace.json references this skill
  if ! grep -q "$skill_name" .claude-plugin/marketplace.json 2>/dev/null; then
    echo "⚠️  $skill_name: Not referenced in marketplace.json"
  fi

  # Check marketplace.json description matches SKILL.md description
  if [[ -f .claude-plugin/marketplace.json ]]; then
    marketplace_desc=$(SKILL_NAME="$skill_name" python3 -c "
import json, os
with open('.claude-plugin/marketplace.json') as f:
  data = json.load(f)
name = os.environ['SKILL_NAME']
for p in data.get('plugins', []):
  if p['name'] == name:
    print(p.get('description', ''))
    break
" 2>/dev/null)

    # Try single-line description first: description: "..."
    skill_desc=$(grep "^description:" "$skill_dir/SKILL.md" | head -1 | sed 's/description: *//; s/^"//; s/"$//')
    # Fall back to multi-line description: > \n  ...
    if [[ -z "$skill_desc" ]]; then
      skill_desc=$(awk '/^description:/{found=1; next} found && /^[^ ]/{exit} found{print}' "$skill_dir/SKILL.md" | tr '\n' ' ' | sed 's/  */ /g; s/^ //; s/ $//')
    fi

    if [[ -n "$marketplace_desc" && -n "$skill_desc" && "$marketplace_desc" != "$skill_desc" ]]; then
      echo "⚠️  $skill_name: marketplace.json description differs from SKILL.md description"
      echo "   marketplace: $marketplace_desc"
      echo "   SKILL.md:    $skill_desc"
    fi
  fi

  echo "✅ $skill_name: Valid"
done

## Validate department entries exist in marketplace.json
if [[ -f .claude-plugin/marketplace.json ]]; then
  for dept_dir in skills/*/; do
    dept_name=$(basename "$dept_dir")
    # Skip departments with no skills
    skill_count=$(find "$dept_dir" -name "SKILL.md" -maxdepth 2 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$skill_count" -eq 0 ]]; then
      continue
    fi
    # Check department-level entry exists in marketplace.json
    dept_in_marketplace=$(DEPT_NAME="$dept_name" python3 -c "
import json, os
with open('.claude-plugin/marketplace.json') as f:
  data = json.load(f)
dept = os.environ['DEPT_NAME']
found = any(p['name'] == dept and len(p.get('skills', [])) > 1 for p in data.get('plugins', []))
print('yes' if found else 'no')
" 2>/dev/null)
    if [[ "$dept_in_marketplace" != "yes" ]]; then
      echo "⚠️  Department '$dept_name' has $skill_count skill(s) but no department entry in marketplace.json"
    fi
  done
fi

if [[ $ERRORS -gt 0 ]]; then
  echo ""
  echo "❌ $ERRORS error(s) found"
  exit 1
fi

echo ""
echo "✅ All skills valid"
