# SLICKK Mail — 100% self-hosted software path on Windows 11

## What self-hosting actually means

Stalwart and Bulwark run on YOUR computer, hold YOUR mailboxes and can communicate using standard SMTP, IMAP and JMAP without a paid mailbox vendor. They are self-hosted open-source components (licensed upstream); the software does not require Gmail, Outlook or a paid mail platform. Internet email is *federated*: it must communicate with recipient domains, DNS infrastructure, your ISP and recipient anti-spam policies. Software cannot mint an Internet-routable IPv4 address, override CGNAT, remove an ISP's port-25 filter, allocate PTR authority or force another mail provider to accept messages.

## No-new-monthly-hosting-cost route (conditional)

This path is feasible ONLY when your existing ISP connection already supplies all of the following:

- A publicly reachable, preferably static IPv4 on your router WAN interface (not `192.168.x.x`, `10.x.x.x`, `172.16-31.x.x`, or CGNAT `100.64-127.x.x`). An adequately delegated and reachable IPv6 address is an advanced alternative; remote IPv4-only MTAs may still need an IPv4 SMTP path.
- Incoming TCP 25 to your router, safely forwarded to the dedicated mail host, plus unblocked outgoing TCP 25. Confirm both from independent networks. Other SMTP ports do not replace server-to-server port 25.
- ISP cooperation for PTR/reverse DNS matching `mail.slickk.online` or delegated reverse-zone control. Your own domain's normal Cloudflare DNS cannot unilaterally set ISP-owned PTR.
- Stable power, uptime, suitable disk, backups, public mail TLS, IP reputation, and permission under your ISP's acceptable-use terms.

If any are missing, no amount of programming the mail server will create them. A clean VPS/colocated server or an SMTP relay is an optional external workaround, but not equivalent to zero-dependency self-hosting. This repo does not force a paid service or silently enable a relay.

## Windows host plan

1. Use Windows 11 SSD and WSL2 Docker Desktop. Keep the 16 GB Ubuntu USB experiment and `cloud.slickk.online` untouched.
2. Run `scripts/windows/Preflight.ps1`; run `scripts/windows/Test-PublicMailReadiness.ps1` READ ONLY (optionally supply public WAN IPv4 read from router settings). Never type Cloudflare API tokens into this script.
3. Start with `compose/local.yaml`. Set up two test accounts under reserved `slickk.test` ONLY; confirm local mailbox send/receive and persistent data.
4. For *public* hosting on the Windows PC, Codex must build a separate secure Windows production deployment profile (not expose the loopback-only local dev stack), enable Windows Firewall rules deliberately, and configure router TCP 25 forwarding only after the network gates pass and user's explicit approval. Verify Docker Desktop/WSL2 port publication, NAT, public hostname and TLS, and that reboot services survive power cycles.
5. Use `mail.slickk.online` as **DNS only** A/AAAA to the publicly routable mail endpoint. `slickk.online` MX then points to that host only after approval and cutover readiness. Ensure DKIM/SPF/DMARC and PTR are real and correct. Do not alter `slickk.online` A/AAAA/CNAME records or `cloud.slickk.online`.
6. Host the user webmail at `inbox.slickk.online` through a separate HTTPS route (a Cloudflare Tunnel is suitable for HTTPS webmail/JMAP, not raw SMTP); protect admin panel. Stalwart's browser JMAP endpoint must also have a valid trusted HTTPS route with proper origin handling.
7. Test from an unrelated internet connection and from *real* outside domains, review original message headers and mail queue, and verify no open relay or spoofing. Treat any failure as a blocker, not success.
8. Store volumes on SSD, back up encrypted off-machine, verify restore, monitor disk, queues, certificate, uptime, and apply security updates with rollback.

## A concrete host feasibility checklist

| Gate | Windows command/check | Proof |
|---|---|---|
| PC can run containers | `docker info` | Linux engine running |
| WAN IP is genuinely public | router WAN IPv4 versus ISP assignment | Not RFC1918 or CGNAT |
| SMTP outgoing | `Test-PublicMailReadiness.ps1 -CheckOutbound25` | TCP handshake, NOT delivery |
| SMTP incoming | Remote non-home network `nc -vz mail.slickk.online 25` after approved forwarding | Connection + server SMTP banner |
| PTR authority | ISP-provided PTR + `Resolve-DnsName <reverse-zone> -Type PTR` | Matches A/mail host |
| DNS authority | Cloudflare existing zone snapshot | No current mail disruption |
| Full roundtrip | Independent Gmail/Outlook actual inbox test | Received, replied, verified SPF/DKIM/DMARC |

**Do not proceed to MX changes before all relevant gates pass.** No component in this repo can allocate an ISP IP or set ISP-owned reverse DNS. Local features can be fully tested regardless of these network blockers.
