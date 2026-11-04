#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
if [[ "${1:-}" != '--authorize-downtime' ]]; then echo 'Usage: bash scripts/linux/backup-offline.sh --authorize-downtime'; exit 2; fi
umask 077
mkdir -p backups
backup_dir="$PWD/backups/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -m 700 "$backup_dir"
docker compose -f compose/production.yaml stop
trap 'docker compose -f compose/production.yaml start' EXIT
for name in stalwart-etc stalwart-data bulwark-data; do
  docker run --rm --mount "type=volume,source=slickk-mail-prod_${name},target=/source,readonly" --mount "type=bind,source=${backup_dir},target=/output" alpine:3.21 sh -c 'cd /source && tar czf "/output/$1.tar.gz" .' _ "$name"
done
(cd "$backup_dir" && sha256sum ./*.tar.gz > SHA256SUMS)
echo 'Backup finished, UNENCRYPTED. Encrypt offsite, then practice restore. Never commit this directory.'
