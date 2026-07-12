#!/usr/bin/env bash
set -euo pipefail

before_snapshot="$(mktemp)"
after_snapshot="$(mktemp)"
trap 'rm -f "$before_snapshot" "$after_snapshot"' EXIT

snapshot_worktree() {
  git diff --binary --no-ext-diff HEAD
  while IFS= read -r -d '' file; do
    printf '%s  %s\n' "$(git hash-object "$file")" "$file"
  done < <(git ls-files --others --exclude-standard -z)
}

snapshot_worktree > "$before_snapshot"

npm run check:ci
git diff --check

snapshot_worktree > "$after_snapshot"
if ! diff -u "$before_snapshot" "$after_snapshot"; then
  echo "Full check mutated the working tree." >&2
  exit 1
fi

echo "Full check passed without working-tree mutations."
