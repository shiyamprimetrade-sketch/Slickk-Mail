# SLICKK Mesh Mail — invention laboratory v0.1

**Purpose:** Verify whether we can build our **own mail addressing and store-and-forward protocol** instead of depending on an existing email operator. This lab uses only Python 3 standard-library code, local SQLite files and sockets. It does not call a third-party mail API.

**Classification:** LOCAL / EXPERIMENTAL, not an internet-ready email provider and not SMTP/IMAP/Gmail compatible. Does not supersede the repository's Stalwart production implementation.

## Launch two independently addressed mailbox nodes on Windows

Open PowerShell in `experiments\meshmail` and enter:

```powershell
py -3 demo.py
```

The script starts two distinct HTTP servers, prints temporary login details **locally**, and opens ports only on `127.0.0.1`:

- `http://127.0.0.1:8097` — login `alice`, address `alice@alpha.local`
- `http://127.0.0.1:8098` — login `bob`, address `bob@beta.local`

Sign in using the printed passwords. Send a message to `bob@beta.local`, open Bob's inbox in another browser window, and reply to `alice@alpha.local`. Data is wiped when the demo exits. Nothing modifies DNS, email MX, Windows networking or existing SLICKK websites.

## Automated tests

```powershell
py -3 -m unittest discover -s experiments/meshmail -p 'test_*.py' -v
```

Linux/macOS: use `python3` instead of `py -3`.

## Persistent-node CLI (developer mode)

```powershell
cd experiments\meshmail
py -3 meshmail.py create-user --node alpha.local --db alpha.db --name alice
py -3 meshmail.py serve --node alpha.local --db alpha.db --port 8097
```

A private password is entered interactively. Local persistent databases should be kept on your SSD and backed up. These labs are local-only. Do not change `--host` to a public interface: v0.1 intentionally blocks that.

## What is implemented and testable

- Local mailbox identities (namespaced as `user@node`), password authentication via scrypt, and login sessions
- Browser inbox, sent folder, compose, search, HTML output escaping, CSRF checks
- Durable SQLite message store and queued outbound transfers
- Direct transport between trusted nodes using timestamp + nonce + HMAC-SHA256 authentication
- Replay detection and idempotent inbox storage
- Retry of queued transfers when a peer becomes reachable
- Test harness with actual socket listeners (no simulated success messages)

## Not implemented / restrictions

- **No internet-wide routing, public IP allocation, or public SMTP.** The lab accepts only loopback peer URLs; an independent network requires a real reachability path (LAN, IPv6, radio mesh, relay owned by us, or another carrier).
- No transport encryption: local HTTP only. HMAC authenticates packets but does **not** hide message contents. DO NOT expose outside the PC or use for sensitive data.
- No attachments, spam scoring, MFA, signup, browser TLS, backups or full Gmail-like feature parity. Production security review and resource enforcement are not complete.
- Neither this lab's address namespace nor `alpha.local`/`beta.local` addresses can receive mail from Gmail without an interoperable SMTP bridge and internet mail routing.

## Scientific test scope

**Hypothesis:** Two self-hosted programs can exchange and retain mailbox messages using our own protocol without a paid mail company.

**Evidence:** Two loopback node processes with actual TCP/HTTP sockets, signed delivery, SQLite persistence and offline queues; tested by `unittest`.

**Unproven:** Global address discovery, NAT traversal, security across untrusted networks, independent global interoperability, physical storage beyond actual media capacity, deliverability and production reliability.

`docs/NETWORK-INVENTION.md` contains the engineering roadmap and boundaries. Build from verified behavior, not from untested assumptions.
