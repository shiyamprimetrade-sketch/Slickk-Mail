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

## WordMind: keyboard-first discovery (Session 02 invention)

The experimental mailbox now includes **WordMind**, an explainable, per-account
word-relationship engine. It builds on the mentor's teaching:

1. Each letter counts as 1: `ABCA` has 4 letters.
2. The count becomes a word: `4 → FOUR`.
3. Apply the rule again: `FOUR → 4 → FOUR`; `APPLE → FIVE → FOUR`.
4. Distinct words are related when they have the same letter count, the same
   letters in another order, or appear near each other in actual messages.
5. Every account can mark a relationship useful/not useful. That feedback changes
   the account's ranking for future discoveries.

### Try it in the browser

After launching `demo.py`, sign in to Alice's and Bob's webmail. Send from Alice
to `bob@beta.local` with subject `ABCA CABA`, and a body such as
`APPLE links to FIVE; FOUR is another way to describe the length`.

At Bob's mailbox, click **WordMind** → search for `ABCA`, `APPLE`, or `FOUR`.
WordMind shows the transformation chain, observed related words, which messages
contained the token, and buttons to teach the ranking with explicit feedback.

### What WordMind has and has not learned

- **Implemented:** symbolic transformations, exact word occurrence, anagram
  recognition, co-occurrence weights, per-user feedback, and a durable private
  SQLite graph derived from messages; newly received messages are indexed once.
- **Not implemented:** true general intelligence, independent invention of
  novel semantics, end-to-end encryption, autonomous network creation, public
  email delivery, or mathematical compression of arbitrary random content.
- **Privacy:** Discovery queries use the authenticated mailbox owner only.
  Message body content is **not** sent to external AI APIs.
- **Storage:** Complete messages remain stored unchanged. The word index uses
  additional finite disk space; the rule does not create limitless storage.
- **Scope:** This is a controlled loopback research prototype, not secure
  internet-facing email software.

Run all tests:

```powershell
py -3 -m unittest discover -s experiments/meshmail -p 'test_*.py' -v
```

Architecture, learning measurements, and test boundaries are in `docs/WORDMIND.md`.
