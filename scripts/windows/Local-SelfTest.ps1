#Requires -Version 5.1
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Set-Location $root
& docker compose -f compose/local.yaml config --quiet
if ($LASTEXITCODE -ne 0) { throw 'Compose validation failed.' }
& docker compose -f compose/local.yaml ps
try {
  $resp=Invoke-WebRequest -Uri 'http://127.0.0.1:3000' -TimeoutSec 12 -UseBasicParsing
  if ($resp.StatusCode -ne 200) { Write-Warning "Webmail status: $($resp.StatusCode)" }
  else { Write-Host 'PASS: Webmail container is serving HTTP locally.' -ForegroundColor Green }
} catch { Write-Warning "Webmail HTTP check failed: $($_.Exception.Message)" }
Write-Host 'Manual gates: Stalwart wizard -> trusted JMAP TLS -> Bulwark wizard -> accounts -> actual send/receive.'
