#Requires -Version 5.1
# System-changing installation is explicitly opted into via -AuthorizeSystemChanges.
param([switch]$AuthorizeSystemChanges)
$ErrorActionPreference = 'Stop'
if (-not $AuthorizeSystemChanges) {
  Write-Host 'Dry run only. To enable WSL2 and install Docker Desktop run:'
  Write-Host '.\scripts\windows\Install-Prerequisites.ps1 -AuthorizeSystemChanges'
  exit 0
}
$admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $admin) { throw 'Open PowerShell as Administrator for this opt-in system change.' }
Write-Host 'Enabling WSL2 (Windows may require restart).'
& wsl.exe --install --no-distribution
if ($LASTEXITCODE -ne 0) { Write-Warning 'WSL installation returned an error. Inspect it before continuing.'; exit 2 }
if (-not (Get-Command winget.exe -ErrorAction SilentlyContinue)) { throw 'winget missing. Install Docker Desktop using https://docs.docker.com/desktop/setup/install/windows-install/ .' }
Write-Host 'Installing Docker Desktop via winget (requires accepting package terms).'
& winget.exe install --id Docker.DockerDesktop --exact --source winget --accept-package-agreements --accept-source-agreements
if ($LASTEXITCODE -ne 0) { Write-Warning 'Docker Desktop installation returned an error; inspect it rather than guessing.'; exit 3 }
Write-Host 'Installation requested. Restart Windows if prompted, start Docker Desktop and ensure WSL2/Linux containers are selected.'
