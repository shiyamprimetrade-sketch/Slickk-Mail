# DNS and deliverability: no automatic changes

## Before any write

Record current `slickk.online` MX, TXT (SPF), DKIM, DMARC, routing and Cloudflare Email Routing settings. The current main website and `cloud.slickk.online` must be untouched. If mail already exists, preserve it pending approved migration.

Only after secure server is deployed and domain cutover approved, likely needed records:

| Record | Name | Value | Notes |
|---|---|---|---|
| A | mail | actual VPS public IPv4 | Cloudflare **DNS only**, never orange-cloud proxy |
| MX | @ | mail.slickk.online, priority selected | Only during approved cutover |
| TXT SPF | @ | derive from real sending systems | Never duplicate SPF records; do not blindly use an example |
| TXT DKIM | generated selector._domainkey | exact public key from Stalwart | Never publish private key |
| TXT DMARC | _dmarc | monitor initially then enforce | Align with senders, avoid premature p=reject |
| PTR | public server IP | mail.slickk.online | VPS provider controls this, not ordinary Cloudflare DNS |
| CNAME/Tunnel | inbox | dedicated HTTPS webmail route | Doesn't replace public SMTP |

Check inbound/outbound port 25, IP reputation and reverse-forward match. Modern providers enforce SPF/DKIM/DMARC and rate limits. Verify received message's original headers (Google/Outlook) instead of assuming delivery from a local SMTP `250 OK`.

### Read-only commands

Windows PowerShell:

```powershell
Resolve-DnsName slickk.online -Type MX
Resolve-DnsName slickk.online -Type TXT
Resolve-DnsName _dmarc.slickk.online -Type TXT
Resolve-DnsName mail.slickk.online -Type A
```

Linux:

```bash
dig +short MX slickk.online
dig +short TXT slickk.online
dig +short TXT _dmarc.slickk.online
dig +short A mail.slickk.online
dig -x YOUR_VPS_IPV4 +short
```

Do not reuse disclosed Cloudflare Tunnel token. Rotate in Cloudflare, then reissue a separate restricted token if a webmail HTTPS tunnel is required.
