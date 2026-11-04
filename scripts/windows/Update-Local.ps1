#Requires -Version 5.1
param([switch]$AuthorizeDowntime)
$ErrorActionPreference='Stop'
if (-not $AuthorizeDowntime) { throw 'Updates require backup + short downtime. Re-run with -AuthorizeDowntime.' }
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
& (Join-Path $PSScriptRoot 'Backup-Local.ps1') -AuthorizeDowntime
if ($LASTEXITCODE -ne 0) { throw 'Backup must succeed before upgrade.' }
Set-Location $root
& docker compose -f compose/local.yaml pull
if ($LASTEXITCODE -ne 0) { throw 'Image pull failed; previous containers remain available.' }
& docker compose -f compose/local.yaml up -d
if ($LASTEXITCODE -ne 0) { throw 'Upgrade failed; inspect logs and restore from backup if needed.' }
& (Join-Path $PSScriptRoot 'Status.ps1')
Write-Host 'Upgrade needs an actual account login + send/receive acceptance test; versions change only when tags are explicitly reviewed.'
