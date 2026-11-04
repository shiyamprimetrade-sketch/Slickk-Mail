# Production deployment runbook — independent SMTP-capable Linux host

**This Compose file targets a Linux host.** For direct Windows self-hosting, read docs/SELF-HOSTING.md and have Codex produce a separate hardened Windows public profile after the IP/ISP gates pass. A VPS is OPTIONAL, not required, if home Internet supports public SMTP and PTR.

## Provider prerequisites

- Static public IPv4, clean IP reputation, inbound+outbound port 25, PTR/reverse DNS configurable, provider accepts email hosting under its terms.
- DNS zone control and existing MX/TXT record snapshot. Confirm no business email service will be disrupted.
- Suggested planning starting size: 2 vCPU, 4 GB RAM, 40+ GB SSD, with future expansion. Actual requirements depend on mail volumes and user activity.
- Secure SSH access, firewall and offsite encrypted backup destination.

On Linux VPS (not Ubuntu USB):

```bash
bash scripts/linux/preflight.sh
bash scripts/linux/deploy.sh --confirm-vps-preflight
docker compose -f compose/production.yaml ps
```

Bootstrap Stalwart via SSH `ssh -L 8080:127.0.0.1:8080 user@VPS_IP`, then open Windows browser `http://127.0.0.1:8080/admin`. Fetch bootstrap admin secret on VPS privately from container logs. Follow https://stalw.art/docs/install/platform/docker/.

During wizard, use `mail.slickk.online` hostname, `slickk.online` domain; obtain valid public TLS certificate. Let the system generate actual DKIM keys and use the generated zone data. Confirm hostname, HTTPS and all mail listeners. Never expose port 8080 outside loopback.

For Bulwark, connect JMAP through `https://mail.slickk.online`, ensure proper cross-origin CORS for HTTPS webmail origin. Publish `inbox.slickk.online` via HTTPS reverse proxy or dedicated tunnel after wizard completed, not before. Configure Cloudflare Tunnel ONLY for the webmail HTTP interface, NOT for incoming SMTP port 25.

Mail DNS instructions in docs/DNS.md. MX change may interrupt current provider; do not perform without approval and fallback plan.

After verifying email send/receive, configure encrypted, offsite backups, monitor queues/storage/cert expiry, restore on staging, rotate leaked credentials, harden server and align policies. Keep Windows local dev and production separate.
