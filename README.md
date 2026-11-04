# SLICKK Mail — Windows 11 + Codex deployment project

**Owner:** SLICKK. **Project boundary:** SLICKK Mail only. Do not conflate with SLICKK Cloud, Slickk-OS, Slickk Pay or other projects.

**Status:** Windows/Linux infrastructure as code and Codex execution specification. Static tests can be run without a Docker engine. **Not yet installed on the user's Windows PC. Mailboxes and external mail delivery NOT verified.**

## What is included

- Windows 11 local test stack: Stalwart mail server + Bulwark webmail in WSL2 Docker containers, using persistent named volumes and loopback-only ports.
- Windows PowerShell preflight, read-only public mail readiness checks, opt-in prerequisites installer, startup, self-test, stop, offline backup and safe upgrade scripts.
- Linux standalone-host production stack, preflight, deployment and backup/update scripts; VPS is optional if a self-hosted public network passes requirements.
- Complete Codex master implementation directive, security policies, DNS and deliverability runbooks, feature matrix, test checklist, and static tests.
- Official upstream dependencies are downloaded from their publishers by Docker. Their source code and binary assets are **not vendored** in this project.

## Zero-subscription self-hosting option

Read `docs/SELF-HOSTING.md`. If the home ISP supplies a public IP, ports and PTR, it is possible to self-host without paying another mail hosting company. Router/ISP/Internet standards still exist. No software can manufacture an assigned public IP or PTR delegation.

## Why two environments?

**Windows local:** You can run and develop SLICKK Mail while preserving Windows 11, using your PC's internal SSD. No 16 GB USB is needed. Windows must stay on and Docker must be running. Network binding is `127.0.0.1`, and no live MX records are touched.

**Self-hosted Internet mail:** If your existing home ISP already provides a routable public IP, working inbound/outbound TCP 25 and suitable PTR authority, Codex can deploy a secured public mail endpoint on your own Windows PC. Run `scripts/windows/Test-PublicMailReadiness.ps1` and read `docs/SELF-HOSTING.md` FIRST. If these gates fail, code cannot allocate an IP or change ISP controls; an external mail-capable host remains an optional alternative, not an automatic purchase. Cloudflare Tunnel handles HTTPS webmail, **not inbound SMTP**.

## First run on Windows (PowerShell)

1. Extract this ZIP to e.g. `C:\SLICKK-Mail-Windows-Codex` on the **Windows SSD**, not the Ubuntu USB.
2. Open Windows PowerShell in that folder (File Explorer address bar: type `powershell` and press Enter).
3. If Docker Desktop/WSL2 are not installed, see `docs/WINDOWS.md` or the opt-in installer below. Startup requires a running Docker Desktop using Linux containers.
4. Run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\scripts\windows\Preflight.ps1
.\scripts\windows\Start-Local.ps1
```

5. Admin first launch: `http://127.0.0.1:8080/admin` (temporary admin credentials in `docker logs slickk-mail-local-stalwart`, *never share*). See `docs/WINDOWS.md` for safe wizard details.
6. Webmail setup: `http://127.0.0.1:3000` (wizard token in `docker logs slickk-mail-local-webmail`, *never share*).
7. **Important:** A fully usable Bulwark client needs a browser-reachable Stalwart JMAP HTTPS endpoint with a trusted certificate and correctly configured CORS; the local project does not pre-provision this. Give the Codex agent `AGENTS.md` and `CODEX_MASTER_PROMPT.md` to implement/verify that integration for the current environment.

## Public mail readiness (read-only)

```powershell
.\scripts\windows\Test-PublicMailReadiness.ps1
# If you have a real public WAN IP shown in your router:
.\scripts\windows\Test-PublicMailReadiness.ps1 -PublicIPv4 "YOUR_ROUTER_PUBLIC_IP" -CheckOutbound25
```

## Have Codex finish the setup

In Codex on this Windows PC, open this project folder and submit:

> Read `AGENTS.md` and `CODEX_MASTER_PROMPT.md` completely. Execute the Windows-local implementation and verification phases. Do not claim internet email delivery unless the independent VPS/DNS/MX/send/receive tests actually pass. Keep existing SLICKK websites and projects unchanged.

Codex must use the real PC's tool access, ask for explicit acceptance of Windows elevation/reboots, provider accounts, DNS cutovers, costs, and secret creation. Do not paste any tokens into chats or source files.

## Important commands

```powershell
.\scripts\windows\Status.ps1
.\scripts\windows\Local-SelfTest.ps1
.\scripts\windows\Backup-Local.ps1 -AuthorizeDowntime
.\scripts\windows\Update-Local.ps1 -AuthorizeDowntime
.\scripts\windows\Stop-Local.ps1
```

Never use `docker compose down -v` on a system with mailboxes: it removes persistent mail data.

## State and non-claims

- Compose, scripts, docs and static validator exist in this ZIP.
- The author's container lacks Windows, Docker Desktop, an authorized public mail endpoint and access to your router/ISP. Windows deployment, JMAP login, mailbox creation, external SMTP and DNS correctness are **not verified**.
- Windows 11 Home is intended to use Linux containers in Docker Desktop with WSL2 if platform/virtualization prerequisites are satisfied.
- The existing Cloudflare Tunnel token from earlier chat was disclosed. Rotate it; never put it in this project.

## Official references

- https://stalw.art/docs/install/platform/docker/
- https://stalw.art/docs/install/platform/windows/
- https://bulwarkmail.org/docs/deployment/docker/compose
- https://bulwarkmail.org/docs/getting-started/installation
- https://docs.docker.com/desktop/setup/install/windows-install/
- https://docs.docker.com/desktop/features/wsl/
- https://developers.cloudflare.com/dns/troubleshooting/email-issues/
