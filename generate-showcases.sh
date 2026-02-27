#!/usr/bin/env bash
# generate-showcases.sh — Regenerate Agent Brain & Raycast Life OS showcase pages
# from their actual source files. Run after adding skills, commands, or services.
#
# Usage:  ./generate-showcases.sh [--agent-brain] [--rlo] [--dry-run]
#         (no args = both)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BRAIN_DIR="$HOME/Dev/agent-brain"
RLO_DIR="$HOME/Dev/raycast-life-os"

DRY_RUN=false
DO_BRAIN=false
DO_RLO=false

for arg in "$@"; do
  case "$arg" in
    --agent-brain) DO_BRAIN=true ;;
    --rlo)         DO_RLO=true ;;
    --dry-run)     DRY_RUN=true ;;
    *)             echo "Unknown arg: $arg"; exit 1 ;;
  esac
done

# Default: do both
if ! $DO_BRAIN && ! $DO_RLO; then
  DO_BRAIN=true
  DO_RLO=true
fi

# ─── AGENT BRAIN ───

count_agent_brain_skills() {
  find "$BRAIN_DIR/skills" -name "SKILL.md" -maxdepth 2 | wc -l | tr -d ' '
}

count_agent_brain_commands() {
  find "$BRAIN_DIR/commands" -name "*.md" -maxdepth 1 | wc -l | tr -d ' '
}

count_agent_brain_scripts() {
  find "$BRAIN_DIR/scripts" -maxdepth 1 -type f | wc -l | tr -d ' '
}

list_agent_brain_skill_clusters() {
  # Returns: cluster_prefix \t count \t display_name
  # e.g.: audit \t 16 \t Audit
  local skills_dir="$BRAIN_DIR/skills"
  for prefix in audit comm dev doc git gh work ledger next; do
    local count
    count=$(find "$skills_dir" -maxdepth 1 -type d -name "${prefix}*" | wc -l | tr -d ' ')
    if [ "$count" -gt 0 ]; then
      echo -e "${prefix}\t${count}"
    fi
  done
}

if $DO_BRAIN; then
  skills=$(count_agent_brain_skills)
  commands=$(count_agent_brain_commands)
  scripts=$(count_agent_brain_scripts)

  echo "Agent Brain: ${skills} skills, ${commands} commands, ${scripts} scripts"

  if $DRY_RUN; then
    echo "[dry-run] Would update ${SCRIPT_DIR}/agent-brain/index.html"
    echo ""
    echo "Skill clusters:"
    for dir in "$BRAIN_DIR/skills"/*/; do
      name=$(basename "$dir")
      desc=""
      if [ -f "$dir/SKILL.md" ]; then
        desc=$(head -5 "$dir/SKILL.md" | grep -i "description\|purpose" | head -1 | sed 's/.*: //' || true)
        if [ -z "$desc" ]; then
          desc=$(sed -n '3p' "$dir/SKILL.md" | sed 's/^[#* ]*//')
        fi
      fi
      printf "  %-30s %s\n" "$name" "$desc"
    done
  else
    echo "  -> Stats updated. To regenerate full HTML, edit the template in this script."
    echo "  -> Current counts: skills=${skills} commands=${commands} scripts=${scripts}"
    # Update stats in existing HTML (sed the numbers in stat-num divs)
    sed -i '' \
      '0,/<div class="stat-num">/{s/<div class="stat-num">[0-9]*/<div class="stat-num">'"${skills}"'/;}' \
      "$SCRIPT_DIR/agent-brain/index.html"
    # Commands stat (second occurrence)
    local_temp=$(mktemp)
    awk -v new="$commands" '
      /stat-num/ { count++ }
      count == 2 && /stat-num/ { sub(/>[0-9]+</, ">" new "<"); count++ }
      { print }
    ' "$SCRIPT_DIR/agent-brain/index.html" > "$local_temp"
    mv "$local_temp" "$SCRIPT_DIR/agent-brain/index.html"
    echo "  -> Updated agent-brain/index.html stat numbers"
  fi
  echo ""
fi

# ─── RAYCAST LIFE OS ───

count_rlo_commands() {
  local pkg="$RLO_DIR/extensions/life-os/package.json"
  if [ -f "$pkg" ]; then
    # Count command entries in package.json
    grep -c '"name":' "$pkg" | tr -d ' '
    # More accurate: count commands array entries
    # python3 -c "import json; print(len(json.load(open('$pkg'))['commands']))" 2>/dev/null || echo "?"
  else
    echo "?"
  fi
}

count_rlo_services() {
  find "$RLO_DIR/packages/core/src/services" -name "*.ts" -maxdepth 1 2>/dev/null | wc -l | tr -d ' '
}

if $DO_RLO; then
  pkg="$RLO_DIR/extensions/life-os/package.json"
  if [ -f "$pkg" ]; then
    commands=$(python3 -c "import json; print(len(json.load(open('$pkg'))['commands']))" 2>/dev/null || echo "?")
    services=$(count_rlo_services)

    echo "Raycast Life OS: ${commands} commands, ${services} services"

    if $DRY_RUN; then
      echo "[dry-run] Would update ${SCRIPT_DIR}/raycast-life-os/index.html"
      echo ""
      echo "Commands by category:"
      python3 -c "
import json
with open('$pkg') as f:
    data = json.load(f)
for cmd in data.get('commands', []):
    print(f\"  {cmd.get('title', '?'):40s} {cmd.get('description', '')[:60]}\")
" 2>/dev/null || echo "  (python3 required for detailed listing)"
    else
      echo "  -> Stats updated."
      # Update the stat number in the RLO page
      sed -i '' \
        '0,/<div class="stat-num">/{s/<div class="stat-num">[0-9]*/<div class="stat-num">'"${commands}"'/;}' \
        "$SCRIPT_DIR/raycast-life-os/index.html"
      echo "  -> Updated raycast-life-os/index.html stat numbers"
    fi
  else
    echo "Raycast Life OS: package.json not found at $pkg"
  fi
  echo ""
fi

echo "Done. Run 'git -C ${SCRIPT_DIR} diff --stat' to see changes."
