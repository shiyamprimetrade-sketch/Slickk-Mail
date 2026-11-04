#Requires -Version 5.1
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Set-Location $root
& docker compose -f compose/local.yaml stop
# Do not run docker compose down -v: that deletes mailboxes.
