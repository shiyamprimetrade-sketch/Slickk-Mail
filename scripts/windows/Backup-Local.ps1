#Requires -Version 5.1
# Stops services for consistent archive. Creates SENSITIVE UNENCRYPTED files.
param([switch]$AuthorizeDowntime)
$ErrorActionPreference='Stop'
if (-not $AuthorizeDowntime) { throw 'Mail service downtime required. Re-run with -AuthorizeDowntime.' }
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Set-Location $root
$ts=(Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$dst=Join-Path $root ("backups\$ts")
New-Item -Path $dst -ItemType Directory -Force | Out-Null
& docker compose -f compose/local.yaml stop
if ($LASTEXITCODE -ne 0) { throw 'Stopping services failed; backup cancelled.' }
try {
  foreach ($name in @('stalwart-etc','stalwart-data','bulwark-data')) {
    $vol="slickk-mail-local_$name"
    & docker run --rm --mount "type=volume,source=$vol,target=/source,readonly" --mount "type=bind,source=$dst,target=/output" alpine:3.21 sh -c 'cd /source && tar czf "/output/$1.tar.gz" .' _ $name
    if ($LASTEXITCODE -ne 0) { throw "Backup failed for $vol" }
  }
  Get-ChildItem "$dst\*.tar.gz" | ForEach-Object { "{0}  {1}" -f (Get-FileHash -Algorithm SHA256 $_.FullName).Hash.ToLower(), $_.Name } | Set-Content (Join-Path $dst 'SHA256SUMS')
  Write-Host "Backup created at $dst. SENSITIVE: encrypt and copy off-machine; verify a restore."
} finally {
  & docker compose -f compose/local.yaml start
}
