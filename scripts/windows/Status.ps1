#Requires -Version 5.1
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Set-Location $root
& docker compose -f compose/local.yaml ps
try {
  $a = Invoke-WebRequest -Uri 'http://127.0.0.1:8080/admin' -TimeoutSec 8 -UseBasicParsing
  Write-Host "Stalwart bootstrap HTTP: $($a.StatusCode)"
} catch { Write-Host "Stalwart bootstrap not responding (normal after setup): $($_.Exception.Message)" }
try {
  $b = Invoke-WebRequest -Uri 'http://127.0.0.1:3000' -TimeoutSec 8 -UseBasicParsing
  Write-Host "Bulwark HTTP: $($b.StatusCode)"
} catch { Write-Warning "Bulwark unavailable: $($_.Exception.Message)" }
