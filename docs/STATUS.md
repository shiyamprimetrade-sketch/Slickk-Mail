# SLICKK Mail status — 2026-11-04

**Execution environment here:** Linux artifact-builder without Windows, PowerShell 5.1, Docker engine, router access, public mail IP or permission to edit DNS. This status records only what has actually been validated here.

| Stage | State | Evidence | Remaining action |
|---|---|---|---|
| Windows-local Compose, scripts and docs | Implemented (source) | `compose/local.yaml`, Windows scripts | Run on owner's Windows PC |
| Self-host public mail readiness diagnostics | Implemented (source) | `Test-PublicMailReadiness.ps1` | Execute on Windows; router WAN/public IP and ISP port25/PTR confirmation |
| Static validation | Passed in builder | `pytest` 6/6; Python YAML parsing; Bash `bash -n` | CI and Docker Compose validation on GitHub runner |
| Windows prerequisites | Unverified | No Windows environment in builder | Check WSL2, virtualization, disk, Docker |
| Stalwart mail service and test accounts | Not running yet | No Docker runtime in builder | Start containers, complete Stalwart wizard, create two local test accounts |
| Bulwark mail UI, trusted JMAP HTTPS | Not verified | Setup wizard must be run on actual host | Configure TLS/JMAP/CORS and test actual login |
| Local self-to-self send/receive | Not verified | No live test accounts | Two-way test messages, attachments, search, retention |
| Public network IP, TCP25, PTR | Unverified / external prerequisites | Code cannot assign ISP IP or PTR | Read-only check then real off-network tests; no MX changes before pass |
| MX/SPF/DKIM/DMARC and external Gmail delivery | Not verified | Domain DNS untouched | Controlled DNS cutover and real delivery/header checks once feasible |
| Backup/restore and security | Backup scripts created, restore unverified | Offline archive scripts | Restore into staging and verify account data, encrypt offsite |

Software source and instructions are provided; **not** a claim that email accounts or public mail delivery are already running.
