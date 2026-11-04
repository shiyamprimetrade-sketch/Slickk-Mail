#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
if [[ "${1:-}" != '--authorize-downtime' ]]; then echo 'Usage: bash scripts/linux/update.sh --authorize-downtime'; exit 2; fi
bash scripts/linux/backup-offline.sh --authorize-downtime
docker compose -f compose/production.yaml pull
docker compose -f compose/production.yaml up -d
docker compose -f compose/production.yaml ps
echo 'Now verify login, mail queue, send AND receive, DNS security and backup restore on staging.'
