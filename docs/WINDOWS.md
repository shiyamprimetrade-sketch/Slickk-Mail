# Windows 11 local installation

## 1. Prerequisites

- Windows 11 x64 with hardware virtualization enabled. Windows 11 Home supports Linux containers via WSL2 on qualifying configurations; confirm official current Docker requirements.
- Recommended >=8 GB RAM and >=20 GB available SSD space (planning minimum, not a measured user machine fact).
- Windows PowerShell, internet and permitted admin elevation for WSL2 / Docker installation.
- Docker Desktop: https://docs.docker.com/desktop/setup/install/windows-install/
- WSL2: https://docs.docker.com/desktop/features/wsl/

Put this project on Windows internal SSD, **not** the 16 GB Ubuntu USB.

## 2. Set up Docker Desktop

Open Windows PowerShell as Administrator only if installing prerequisites:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\scripts\windows\Install-Prerequisites.ps1 -AuthorizeSystemChanges
```

This may require user approval and Windows restart. Start Docker Desktop, select Linux containers and WSL2 backend. Do not automatically reboot or forcibly close apps.

For preinstalled Docker:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\scripts\windows\Preflight.ps1
.\scripts\windows\Start-Local.ps1
```

**Service addresses:**

- Stalwart initial setup `http://127.0.0.1:8080/admin` (loopback only). Run `docker logs slickk-mail-local-stalwart` locally to find temporary admin password. It is a secret. Complete wizard for TEST ONLY (`mail.slickk.test`, `slickk.test`) and restart `docker compose -f compose/local.yaml restart stalwart`.
- Bulwark initial setup `http://127.0.0.1:3000`. Run `docker logs slickk-mail-local-webmail` to find the one-time setup token. Use its setup wizard.
- Stalwart HTTPS mapping `https://127.0.0.1:8443` needs hostname/certificate setup; **DO NOT bypass browser TLS warnings**. Codex is responsible for implementing a trusted local dev certificate and documenting CORS/JMAP before claiming usable webmail. A working Docker container is NOT proof of working mail.

The Bulwark wizard may refuse a JMAP server without correctly configured HTTPS. That's expected until certificate/trusted hostname configuration is finished. Stalwart's post-setup admin expects HTTPS on its configured hostname.

## 3. Operations

```powershell
.\scripts\windows\Status.ps1
.\scripts\windows\Local-SelfTest.ps1
.\scripts\windows\Backup-Local.ps1 -AuthorizeDowntime
.\scripts\windows\Update-Local.ps1 -AuthorizeDowntime
.\scripts\windows\Stop-Local.ps1
```

Backups are NOT encrypted: treat as confidential until encrypted. Any `down -v` or manual Docker volume delete would irreversibly delete mailbox data. Keep backups off the SSD and practice staging restore.

## 4. Windows-local limitation

Docker Desktop does not itself provide a static public IP, usable inbound/outbound port 25 or reverse DNS. No real external email delivery is guaranteed. Do not change MX while local tests are incomplete.
