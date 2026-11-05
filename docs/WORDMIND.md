# SLICKK Mail WordMind — Keyboard-First Mailbox Invention

**Status:** Working experimental implementation with Python 3 standard library; local-only.
**Project:** SLICKK Mail (not SLICKK-OS / ET INTERNET / SLICKK Cloud).
**Owner-defined learning principle:** Each letter counts as 1. Words transform
into numbers and number-words. Each word's meaning and function should be
investigated through interactions with other words.

## Purpose

A mailbox is a practical environment in which words interact through real
communication. Rather than treating the inbox as a static folder tree, WordMind
builds a small, explainable relationship graph from actual messages. Users can
teach it which associations are useful. All data and logic stay on the host.

## Algorithm v0.1

1. Normalize ASCII keyboard letters A-Z and count letters individually.
2. Transform length to English number word (`ABCA → FOUR`; `APPLE → FIVE → FOUR`).
3. On incoming and sent mail, tokenize subject/body and store bounded word counts
   and a graph of words observed up to four contextual positions apart.
4. Link words of equal length, anagrams and previously observed co-occurrences.
   Show reasons for every recommendation.
5. Store a per-user positive/negative relevance preference. User feedback changes
   future ranking, with no other user's mailbox messages exposed.
6. Reindex old messages idempotently: adding WordMind does not destroy existing mail.

The engine is deterministic and deliberately simple. It does not yet infer
arbitrary semantic meaning or generate executable behaviors for each word. It is
a measurable starting point for research into emergent word interactions.

## Proof and falsifiability

Run:

```sh
python -m unittest discover -s experiments/meshmail -p 'test_*.py' -v
```

Acceptance criteria:
- `ABCA` decomposes into four unit letters and maps to `FOUR`.
- `APPLE` maps `APPLE → FIVE → FOUR` and reaches a fixed point.
- When `ABCA` and `CABA` appear together, the relationship explains letter count,
  anagram match, and nearby co-occurrence.
- Explicit feedback measurably changes relevance scoring.
- Queries from one account do not retrieve another account's message content.
- Existing message data is reindexed exactly once; index survives reconnect.
- CSRF protection applies to feedback and user authentication gates discovery.

## Known limitations / next experiments

- **Current learning:** frequency accumulation + user feedback; no unsupervised
  semantic discovery guarantee, no general intelligence claim.
- **Scalability:** bounded per-message indexing (160 words, 96 contextual tokens).
  Evaluate database size, search latency and candidate recall at 1K/100K mails.
- **Privacy:** messages reside locally in SQLite without encryption-at-rest in
  this lab. Never load real private mail into the prototype without hardening.
- **Transport:** Mesh Mail nodes only support trusted localhost HTTP. No SMTP
  compatibility, mobile cross-network exposure, or public address delegation.
- **Physical resources:** a compact rule may generate structured data; it cannot
  reconstruct arbitrary unpredictable content without retaining adequate
  information. Data capacity and computation remain measurable physical resources.

## Next research milestones

- Better language handling: Unicode, punctuation, numbers and symbol keys.
- Semantic evaluation: labeled human examples; benchmark whether adaptive links
  beat word-count and exact-keyword baselines.
- Formal word-function discovery: give words executable but sandboxed behaviors
  learned from reward/evidence, never privileged OS access by default.
- Message export and recovery tests; encrypted storage and secure trusted peers.
- Design a practical email bridge separately from experimental word discovery.
