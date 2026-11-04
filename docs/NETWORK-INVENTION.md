# SLICKK Mail — Independent Networking Research Track

Status: `PROTOTYPE / LOCAL TESTED` — this is an **additional** research track, separate from normal SMTP/JMAP mail deployment.

## Inventor's challenge

Can we control our own *identity layer*, *mail protocol*, *message storage*, *delivery scheduling* and *inter-node routing*, while minimizing paid services and respecting the actual hardware/network properties? Yes, and `experiments/meshmail` implements the first verifiable stage.

### Distinguish software conventions from physical/institutional constraints

| Element | Can our code define it? | Observable constraint |
| --- | --- | --- |
| Mail address such as `alice@node` | Yes | Our own clients must understand it; Gmail won't automatically route it |
| Packet format and mailbox database | Yes | Both endpoints must agree on wire format and authenticate peers |
| Overlay address / private IPv4 / IPv6 ULA | Yes | Address exists in our overlay but doesn't become globally reachable by naming alone |
| Public Internet-routable IPv4/IPv6 | Cannot simply assign it to ourselves | Upstream routers must forward traffic to the address; conflicts are filtered |
| Reverse DNS visible to other mail servers | Can implement our own reverse-DNS service | Public reverse DNS requires delegation by the reverse-zone operator |
| Physical flash capacity | Can encode/compress/deduplicate bytes | Bytes still occupy a finite number of memory cells; compression ratios depend on content |
| Storage quotas | Yes | Changing a quota does not increase measured capacity; storage full must be handled safely |
| Independent local radio/Wi-Fi mesh | Yes, with compatible hardware | Coverage limited by distance, power, interference and relay participation |
| Internet email interoperability | Yes, by implementing open protocols | Other servers need a reachable SMTP endpoint and domain-to-host mail routing |

## Research phases and gates

**Phase A — independent mailbox protocol (implemented):** Each node has local identities, password-based login, mailbox database, message serialization, signed messages, deduplication, offline queue and retry. Gate: two nodes exchange messages and data persists across reopening database. Verify with `python -m unittest discover -s experiments/meshmail -v`.

**Phase B — LAN-first multi-device network:** Add authenticated HTTPS between PC and Samsung, end-to-end message encryption, independently generated key pairs, mDNS/discovery within home network, sender trust, expiry, throttling and encrypted backup. Gate: physical Windows and Samsung devices exchange encrypted messages without a provider. Do not use v0.1 in public; no TLS is present yet.

**Phase C — decentralized routing:** Introduce stable node IDs (public keys), a signed peer directory, store-and-forward relays, configurable route scoring, expiration and local peer discovery. Implement alternate transports: direct IPv6 when available, LAN, owned Wi-Fi/radio mesh, and optional gateways. Gate: nodes can deliver after one disconnect/reconnect and without a single required coordinator **in a test environment**. Every relay consumes actual bandwidth and power; record metrics.

**Phase D — inter-network path experiments:** Determine which real connectivity paths exist on the user's owned network: public IPv6, IPv4 with port forwarding, upstream CGNAT, independent radio gateway, or a reciprocal peer relay. Test reachability from two **different network providers**. An overlay can conceal or replace address conventions but cannot force upstream operators to forward traffic. Gate: remote devices exchange signed data after NAT/router/ISP behavior is measured, without pretending reachability.

**Phase E — optional standard mail bridge:** Keep SLICKK-native network separate from the real `slickk.online` mail domain, then add a standards-compliant SMTP/MX/DKIM/DMARC gateway **only where an actual inbound SMTP route exists**. Gate: external Gmail mail received and replied to with independent headers and anti-abuse tests. Nothing about Phase A implies Phase E has passed.

**Phase F — capacity experiments:** Add compression and deduplication, measure real bytes written/read and end-to-end latency, vary content entropy, validate recovery after disk-full or power loss. Target measurable efficiency gains rather than claiming a 16 GB device can have arbitrary capacity.

## Control and safety

- Keep current `slickk.online` and `cloud.slickk.online` intact.
- Do not enable public signup, configure MX, expose SMTP or open router ports automatically.
- Use the existing SLICKK Mail GitHub repository for code, tests and evidence only; never commit passwords, private keys, Cloudflare tunnel tokens or private emails.
- A successful demo requires output/logs and an actual API/network exchange, not only a green screenshot.
- Stay zero-subscription by default. Optional paid infrastructure is a separate decision after tested alternatives.

## Codex continuation directive

Role: Research Engineer + Protocol Designer + Network Engineer + Security Engineer + QA Engineer.

Continue from `experiments/meshmail` **without replacing existing Stalwart production track**. Run tests, fix defects, implement Phase B with real authenticated transport security, add reproducible Windows/Samsung tests, and measure connection feasibility. Never call a node 'public' until independent-network reachability is observed. Maintain `docs/STATUS.md`, preserve commits and stop after reporting actual evidence for each stage.
