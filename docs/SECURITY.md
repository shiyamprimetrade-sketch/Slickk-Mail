# Security gates

- Never create public account registration without verification, human abuse review, rate limits, temporary account limits, quotas and logging. Invite-only by default.
- Use modern password hashing managed by upstream, MFA, secure recovery, admin role separation and login lockout. Do not dump passwords in logs or plaintext configs.
- Require TLS for credentials. No disabling cert validation, no HTTP admin exposed outside loopback. Webmail HTTPS also requires JMAP HTTPS and correct CORS.
- Stalwart must require authenticated user submission and prevent open-relay behavior. Test external unauthenticated relay rejection safely.
- Protect against malicious attachments (limits, detection, allow safe downloads), XSS/CSRF/session theft, phishing and spoofing. Review file MIME sanitization and HTML display controls.
- Protect SPF/DKIM/DMARC and incoming spam filtering; mailbox quota, recipient rate limits, egress rate and abuse workflows.
- API tokens in OS-secure storage; do not commit `.env`, Cloudflare tunnel tokens, private keys, sample user passwords, mail headers, logs with addresses, or backups.
- Rotate previously shared Cloudflare token before private emails; incident process records the fact of exposure, not the credential itself.
- Backups contain private mail: encrypt, store offsite, regularly restore into isolated staging environment, retain minimum required data under relevant laws.
- Never delete volumes, overwrite domain MX, disable firewall, or publish bootstrap mode as a convenient shortcut.
