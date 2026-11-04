# CODEX MASTER EXECUTION DIRECTIVE — SLICKK MAIL (WINDOWS 11 + PRODUCTION)

You are Codex operating ON THE USER'S WINDOWS 11 PC with permission to work in THIS SLICKK Mail repository. Build and verify a usable independent email product named **SLICKK Mail**. You are an executing engineer, not an advisory chatbot. Execute all feasible reversible local changes, tests and fixes now; preserve working code and state across sessions. Separate the app from Slickk Cloud, Slickk Pay, Slickk-OS, and every other project.

## Mission and goals

1. Users can create/obtain approved addresses on the owned `slickk.online` domain, authenticate, compose, send, receive, reply, reply-all, forward, search, star/flag, archive, organize folders/labels, draft, trash, spam, upload/download attachments, manage contacts and calendar, signatures, filters, vacation responder, notification preferences, mobile browser/PWA, account security, mailbox quotas, aliases, and profiles.
2. Admin can invite/create/suspend users, configure domain and aliases, approve registrations, reset accounts safely, set role-based permissions, retention/limits/anti-abuse, see audit logs, manage secure backups and updates.
3. Support authenticated SMTP/IMAP/JMAP clients (including Samsung mail apps), TLS, SPF/DKIM/DMARC, bounce/queue handling, anti-spam/anti-phishing, delivery logs and email search. Avoid open relay and user enumeration.
4. Use **Stalwart** for the actual mail server and **Bulwark** for usable webmail; customize styling and extend missing features with documented APIs only. Preserve license compliance and upstream maintenance. Do not falsely claim exact Google/Gmail parity (proprietary AI and integrations are not part of this requirement).
5. Provide a Windows **local functional deployment** AND a secure **self-hosted Windows external SMTP deployment path if the ISP/network passes all infrastructure gates**; alternatively prepare a mail-capable Linux standalone host. No paid provider is mandatory if the home network can genuinely support inbound/outbound SMTP and PTR. Never confuse a local webmail demonstration with verified external email delivery.

## Known environment

- Windows 11 Home PC, x86_64 presumed but detect it; BIOS UEFI. Keep Windows intact. Existing 16 GB Ubuntu USB is a separate experimental web host with only 4 GB persistence; do NOT install mailboxes there.
- Domain `slickk.online` already has a website; `cloud.slickk.online` already runs a Cloudflare Tunnel to an experimental Nginx site. Do not alter them.
- Desired mail hostname: `mail.slickk.online` (DNS-only mail host, external SMTP), webmail: `inbox.slickk.online` (HTTPS application), addresses `hello@`, `support@`, `admin@` as examples only. Do not create these as real accounts until admin and domain setup ready.
- Existing Cloudflare Tunnel token was pasted in conversation and must be regarded as disclosed, not reused in any stored file. Treat all existing external DNS/email records as unknown until read.
- First action: inspect Windows available RAM, free disk, virtualization, WSL2, Docker Desktop, network, current MX/TXT/A/CNAME and whether any email service already exists. Record actual values, never guess.

## Engineering stack and artifacts

- Windows PowerShell 5.1+, WSL2, Docker Desktop Linux containers, Docker Compose, pinned Stalwart 1.x, pinned Bulwark compatible release, Python 3 for static tests/tooling, Bash for VPS operations.
- Keep local ports on 127.0.0.1. Use named persistent volumes on the internal SSD.
- Preserve `compose/local.yaml`, `compose/production.yaml` and current implementation unless evidence supports a change. Use source code with clear tests, not inert mockups as final proof.
- Use Stalwart internal accounts unless approved migration to existing directory. Use OAuth/OIDC only after provider configuration is proven.
- Build optional SLICKK branding assets/configs only without removing production webmail features. Extend via documented plugin APIs when supported, not hacks that break upgrades.

## Phase 0 — Audit and checkpoint

- Read AGENTS.md + README and all docs. Confirm exact runtime, Docker engine, DNS, current services, available resources and disk safety.
- Create docs/STATUS.md with table: task, state, test command, evidence, blockers, next; keep it updated.
- Inventory supported features from current official Bulwark/Stalwart docs and map to `docs/FEATURES.md`. Identify features needing code rather than claiming unsupported functionality.
- Run static tests before editing. Commit checkpoint to a NEW mail-only Git branch if repository exists; do not push to unrelated repositories.

## Phase 1 — Working Windows local installation

- If WSL2/Docker missing, automate their installation using official Windows/Docker packages only and *explicitly approved* admin elevation/reboot. Never force reboot without approval. Detect Home/CPU/virtualization limitations; offer a native Windows Stalwart path if Docker cannot run (official Stalwart Windows install + Bulwark runtime).
- Use `scripts/windows/Start-Local.ps1`. Validate compose and pull version-pinned images. Docker starts via Windows; do not erase volumes.
- Complete Stalwart first-run setup in private loopback. Prefer documented bootstrap API for automation after inspecting exact protocol schema; otherwise use wizard and clearly explain necessary credentials and choices. Set a TEST-ONLY mail domain `slickk.test` for local isolated tests (do not accidentally route `slickk.online` MX). Use strong admin passwords, no password in repository.
- Ensure local browser-to-Stalwart JMAP has a valid HTTPS/CA trust story and CORS using the upstream docs. Implement deterministic local TLS setup (for example, a named localhost development domain and user-trusted local CA, not TLS validation bypass) and tests. If impossible on the machine, record exact blocker.
- Finish Bulwark setup through its wizard or documented provisioning API. Verify actual user login, mailbox operations, search, attachments, contacts and calendar where supported. Prove at least 2 accounts can exchange locally through supported APIs, without relying on external SMTP.
- Add Windows Start/Stop/Status/Backup/Update/Restore-to-staging/Log-redaction/Test scripts. Make updates reversible, back up before pulling new images. Ensure data survives container and machine restart.

## Phase 2 — Feature completion and product quality

- Create an explicit Gmail-like feature matrix, verify each behavior by integration/UI tests. Differentiate native upstream, own extension code, and missing proprietary features.
- Implement a SLICKK-branded signup/invite flow *disabled for public access by default*; registration validation, account approval, email verification where safe, CSRF/session controls, CAPTCHA/rate limits, abuse controls, audit events, MFA, recovery (using supported Stalwart APIs). Never enable anonymous public mailbox creation without abuse prevention and admin consent.
- Enforce role separation; prevent privilege escalation, injection/XSS, open redirect, attachment bypass, data leakage, email spoofing and open SMTP relay.
- Make mobile experience accessible/responsive. Confirm normal Samsung browser use; add PWA support only if stable in chosen upstream.
- Write tests for accounts, authentication, compose restrictions, basic email transactions, backup integrity, TLS/CORS and failure recovery. Tests must fail clearly if prerequisites are absent.

## Phase 3 — Real external delivery infrastructure (SELF-HOST FIRST; READ-ONLY NETWORK AUDIT)

- Inspect existing `slickk.online` MX/TXT records READ ONLY. If existing email is hosted elsewhere, preserve it until explicit planned cutover.
- Run scripts/windows/Test-PublicMailReadiness.ps1 and inspect router WAN IP (do not expose private router credentials). Determine if home self-hosting meets publicly routable IPv4, inbound AND outbound TCP 25, ISP PTR authority, stable uptime, domain reputation and TLS. If all pass, implement a secure Windows-hosted production profile with explicit firewall and router forwarding approvals; independent external testing is mandatory. If not, document the blockers and offer a Linux host as optional fallback; NEVER fabricate a public IP, pretend to change ISP-owned reverse DNS, or buy anything.
- User must authorize provider purchase/cost, hosting credentials, DNS mutations, MX changes and any risky production action. Do not invent account access, network capabilities or payments.
- Deploy `compose/production.yaml` to an appropriately sized host with publicly routable SMTP after preflight; on Windows first implement and test a secure public-host profile rather than exposing the local-only development stack. Secure bootstrap via SSH loopback, configure host `mail.slickk.online`, domain, certificates and DNS-only A record, PTR via provider, DKIM from REAL generated key, SPF, DMARC monitoring, MTA-STS as appropriate, IPv6 only if correctly configured. Configure firewall, logs, rate limits, quotas and monitoring. Avoid using HTTP Cloudflare Tunnel for SMTP ingress.
- Expose `inbox.slickk.online` through HTTPS reverse proxy or dedicated Cloudflare Tunnel AFTER webmail is initialized. The browser-accessible JMAP `https://mail.slickk.online` must have valid TLS and correct CORS to the webmail origin. Existing `cloud.slickk.online` stays unchanged.
- No MX switch until: baseline DNS snapshot, valid certificate, incoming SMTP endpoint, domain accounts created, spam protection, backup, queue checks and explicit authorization.
- Real acceptance test: from an independent Gmail address send to user mailbox, receive, reply, verify outbound placement and headers SPF/DKIM/DMARC; repeat with Outlook if available, investigate bounces. Verify service restart and restore on independent staging VPS.

## Phase 4 — Reliability, security and upgrades

- Version-pin and license-check all dependencies; use compatibility review before updates. Snapshot encrypted, off-host and VERIFY restore before live upgrades. Add alerting: uptime, TLS expiration, SMTP queue, disk, storage, abuse spike, delivery rejects, login failures, backup freshness.
- Create secure registration governance, retention policy, privacy disclosure and anti-spam abuse contact appropriate to the mail provider. Detect and prevent bulk/spam use of new accounts. Implement incident token rotation (old tunnel token is already disclosed).
- Performance tests: simultaneous logins, IMAP sync, search latency, large attachment limits, restart/retention, disk exhaustion; quantify results.
- Produce usable operator docs and one-command safe Windows launch. Build packaged release with user-tested steps and rollback.

## Required evidence / stop criteria

Report state after each phase: role; files changed; commands actually run; tests pass/fail; evidence; blockers and next precise command. Local completion requires real account login, local mail exchange, persistent data, secure browser connection and tested backup/restore. Public completion REQUIRES successful external exchange, DNS authentication passes and secured, recoverable hosting. NEVER fabricate tests, never label open dependencies as successful. If provider/DNS credentials are missing, finish all local work and pause only those external dependencies.

Begin now with Phase 0 and Phase 1, executing code and tests on this Windows PC, preserving all existing SLICKK services and data. The user prefers ZERO new hosting fees: pursue direct home hosting when external infrastructure requirements can actually be met, and label unavailable requirements as verified blockers.
