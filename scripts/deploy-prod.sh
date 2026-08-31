#!/usr/bin/env bash
set -euo pipefail

vercel=(npx --yes vercel@55.0.0)
expected_project_id="prj_zckfhKgH11wFJDTH6NFDaxrX2blp"

"${vercel[@]}" link \
  --yes \
  --scope viggos-projects-eac4720a \
  --project viggomeesters.nl

python3 -c 'import json, pathlib, sys; data=json.loads(pathlib.Path(".vercel/project.json").read_text()); expected=sys.argv[1]; actual=data.get("projectId"); assert actual == expected, f"Refusing production deploy: expected Vercel project {expected}, got {actual!r}"' "$expected_project_id"

"${vercel[@]}" deploy --prod --yes
