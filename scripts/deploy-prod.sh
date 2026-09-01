#!/usr/bin/env bash
set -euo pipefail

vercel=(npx --yes vercel@55.0.0)
scope="viggos-projects-eac4720a"
expected_project_name="viggomeesters.nl"
expected_project_id="prj_zckfhKgH11wFJDTH6NFDaxrX2blp"
expected_org_id="team_Mr9h6NsB9A8GONSuzdZue511"
project_metadata="$(mktemp /tmp/viggomeesters-vercel-project.XXXXXX.json)"

cleanup() {
  rm -f "$project_metadata"
}
trap cleanup EXIT

"${vercel[@]}" api "/v9/projects/$expected_project_id" \
  --scope "$scope" \
  --raw > "$project_metadata"

mapfile -t verified_binding < <(
  python3 - "$project_metadata" "$expected_project_id" "$expected_project_name" "$expected_org_id" <<'PY'
import json
import pathlib
import sys

metadata_path = pathlib.Path(sys.argv[1])
expected_id = sys.argv[2]
expected_name = sys.argv[3]
expected_org_id = sys.argv[4]
data = json.loads(metadata_path.read_text(encoding="utf-8"))
actual_id = data.get("id")
actual_name = data.get("name")
org_id = data.get("accountId") or data.get("teamId")
if actual_id != expected_id:
    raise SystemExit(
        f"Refusing production deploy: expected Vercel project {expected_id}, got {actual_id!r}"
    )
if actual_name != expected_name:
    raise SystemExit(
        f"Refusing production deploy: expected project name {expected_name!r}, got {actual_name!r}"
    )
if org_id != expected_org_id:
    raise SystemExit(
        f"Refusing production deploy: expected Vercel team {expected_org_id}, got {org_id!r}"
    )
print(actual_id)
print(org_id)
PY
)

if [[ "${#verified_binding[@]}" -ne 2 ]]; then
  echo "Refusing production deploy: incomplete verified Vercel binding" >&2
  exit 1
fi

export VERCEL_PROJECT_ID="${verified_binding[0]}"
export VERCEL_ORG_ID="${verified_binding[1]}"

"${vercel[@]}" deploy --prod --yes --scope "$scope"
