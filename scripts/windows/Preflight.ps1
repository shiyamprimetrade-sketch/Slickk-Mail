#Requires -Version 5.1
# Read-only diagnostics. Run in Windows PowerShell or PowerShell 7.
$ErrorActionPreference = 'Stop'
Write-Host '=== SLICKK Mail Windows preflight ==='
$os = Get-CimInstance Win32_OperatingSystem
$cs = Get-CimInstance Win32_ComputerSystem
$ramGB = [math]::Round($cs.TotalPhysicalMemory / 1GB,1)
Write-Host ('Operating system: ' + $os.Caption)
Write-Host ('Physical RAM: ' + $ramGB + ' GB')
$drive = Get-PSDrive -Name C -ErrorAction SilentlyContinue
if ($drive) { Write-Host ('C: free: ' + [math]::Round($drive.Free / 1GB,1) + ' GB') }
if ($ramGB -lt 8) { Write-Warning 'Docker Desktop WSL2 may not run reliably with less than 8 GB RAM.' }
if ($drive -and $drive.Free -lt 20GB) { Write-Warning '20+ GB free on your internal SSD is recommended. Do not store mail volumes on the 16 GB live USB.' }
$wsl = Get-Command wsl.exe -ErrorAction SilentlyContinue
if ($wsl) { Write-Host 'WSL tool: present'; & wsl.exe --status 2>&1 | Select-Object -First 8 } else { Write-Warning 'WSL tool not found.' }
$docker = Get-Command docker -ErrorAction SilentlyContinue
if (-not $docker) { Write-Warning 'Docker CLI missing. Install Docker Desktop for Windows with WSL2 backend.'; exit 2 }
& docker --version
& docker compose version
& docker info --format '{{.OSType}}' 2>$null
if ($LASTEXITCODE -ne 0) { Write-Warning 'Docker engine is not running. Start Docker Desktop and retry.'; exit 3 }
if ((& docker info --format '{{.OSType}}') -ne 'linux') { throw 'Switch Docker Desktop to Linux containers / WSL2 backend.' }
Write-Host 'Preflight complete: Linux container engine available.' -ForegroundColor Green
