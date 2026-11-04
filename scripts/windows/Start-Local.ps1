#Requires -Version 5.1
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
& (Join-Path $PSScriptRoot 'Preflight.ps1')
if ($LASTEXITCODE -ne 0) { throw 'Preflight failed. Start Docker Desktop (Linux/WSL2) before trying again.' }
Set-Location $root
& docker compose -f compose/local.yaml config --quiet
if ($LASTEXITCODE -ne 0) { throw 'Compose configuration invalid.' }
& docker compose -f compose/local.yaml up -d
if ($LASTEXITCODE -ne 0) { throw 'Containers failed to start. Check logs with docker compose -f compose/local.yaml logs.' }
& docker compose -f compose/local.yaml ps
Write-Host 'Local endpoints: http://127.0.0.1:8080/admin (Stalwart bootstrap); http://127.0.0.1:3000 (Bulwark wizard)'
Write-Host 'Setup tokens and bootstrap passwords are in container logs. Keep them private.'
Write-Host 'This is LOCAL ONLY. Trusted JMAP HTTPS/CORS configuration is needed for full browser email features.'
