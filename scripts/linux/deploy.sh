#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
if [[ "${1:-}" != '--confirm-vps-preflight' ]]; then
 echo 'Read docs/PRODUCTION.md. Run: bash scripts/linux/deploy.sh --confirm-vps-preflight'; exit 2
fi
if [[ -d /cow ]]; then echo 'Refusing deployment on live USB'; exit 3; fi
bash scripts/linux/preflight.sh
docker compose -f compose/production.yaml config --quiet
docker compose -f compose/production.yaml up -d
docker compose -f compose/production.yaml ps
echo 'Containers started; complete secure setup wizard, DNS and delivery tests before claiming production.'
