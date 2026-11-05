"""SLICKK WordMind v0.1: explainable, owner-private symbolic mailbox discovery.

This is an experimental, deterministic learning layer for local Mesh Mail.
It learns co-occurrences and user feedback; it does NOT understand semantics like
an LLM, allocate physical storage, or guarantee that symbols encode every input.
No external services or third-party libraries are used.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import re
from urllib.parse import quote

TOKEN_RE = re.compile(r"[A-Za-z]+")
MAX_WORD = 32
MAX_DOCUMENT_WORDS = 160
MAX_CONTEXT_WORDS = 96
WINDOW = 4
STOP_WORDS = frozenset("a an the and or to in on at from for with of is are was were it this that i you me my your be by we us as not can will have has had do does did our their his her she he they they them how why when where who what".split())
ONES = ("ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE", "TEN", "ELEVEN", "TWELVE", "THIRTEEN", "FOURTEEN", "FIFTEEN", "SIXTEEN", "SEVENTEEN", "EIGHTEEN", "NINETEEN")
TENS = ("", "", "TWENTY", "THIRTY", "FORTY", "FIFTY", "SIXTY", "SEVENTY", "EIGHTY", "NINETY")


def count_word(n: int) -> str:
    """Spell 0..9999 in English; outputs alphabetic uppercase words separated by spaces."""
    if not isinstance(n, int) or isinstance(n, bool) or n < 0 or n > 9999:
        raise ValueError("word length out of supported range (0-9999)")
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + (" " + ONES[n % 10] if n % 10 else "")
    if n < 1000:
        return ONES[n // 100] + " HUNDRED" + (" " + count_word(n % 100) if n % 100 else "")
    return ONES[n // 1000] + " THOUSAND" + (" " + count_word(n % 1000) if n % 1000 else "")


def normalize_word(value: str) -> str:
    value = value.strip().lower()
    if not value or len(value) > MAX_WORD or not value.isascii() or not value.isalpha():
        raise ValueError("Use one alphabetic word, up to 32 letters")
    return value


def word_identity(value: str) -> dict:
    """A→1 per letter, WORD→letter count→English count-word; deterministic relation."""
    word = normalize_word(value)
    return {"word": word, "letters": list(word.upper()), "length": len(word),
            "number_word": count_word(len(word)), "signature": "".join(sorted(word))}


def word_chain(value: str, max_steps: int = 12) -> list[str]:
    """Derive words from their letter-count words until a repeat or safety limit.

    Example: APPLE -> FIVE -> FOUR; ABCA -> FOUR. Convergence is an
    observed English spelling property, not evidence of cognition.
    """
    first = normalize_word(value).upper()
    trace = [first]
    seen = {first}
    for _ in range(max_steps):
        current_letters = sum(c.isalpha() for c in trace[-1])
        nxt = count_word(current_letters)
        if nxt in seen:
            break
        trace.append(nxt)
        seen.add(nxt)
    return trace


def extract_words(text: str) -> list[str]:
    return [w.lower() for w in TOKEN_RE.findall(text) if 2 <= len(w) <= MAX_WORD][:MAX_DOCUMENT_WORDS]


class WordMind:
    """All queries are scoped to a specific mailbox owner. SQLite-backed; no cloud API."""

    def __init__(self, conn):
        self.conn = conn
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS mind_docs (
          message_id TEXT PRIMARY KEY, owner TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS mind_words (
          owner TEXT NOT NULL, word TEXT NOT NULL, length INTEGER NOT NULL,
          signature TEXT NOT NULL, observed INTEGER NOT NULL DEFAULT 0,
          PRIMARY KEY(owner,word)
        );
        CREATE INDEX IF NOT EXISTS idx_mind_length ON mind_words(owner,length,observed DESC);
        CREATE INDEX IF NOT EXISTS idx_mind_signature ON mind_words(owner,signature);
        CREATE TABLE IF NOT EXISTS mind_document_words (
          owner TEXT NOT NULL, message_id TEXT NOT NULL, word TEXT NOT NULL,
          frequency INTEGER NOT NULL,
          PRIMARY KEY(owner,message_id,word)
        );
        CREATE INDEX IF NOT EXISTS idx_mind_search ON mind_document_words(owner,word);
        CREATE TABLE IF NOT EXISTS mind_context (
          owner TEXT NOT NULL, source TEXT NOT NULL, target TEXT NOT NULL,
          weight INTEGER NOT NULL,
          PRIMARY KEY(owner,source,target)
        );
        CREATE TABLE IF NOT EXISTS mind_feedback (
          owner TEXT NOT NULL, source TEXT NOT NULL, target TEXT NOT NULL,
          preference INTEGER NOT NULL CHECK(preference IN (-1,1)),
          PRIMARY KEY(owner,source,target)
        );
        """)
        conn.commit()

    def index_mail(self, owner: str, message_id: str, subject: str, body: str) -> bool:
        """Index once per mailbox copy. Caller handles SQLite transaction and thread lock."""
        cur = self.conn.execute("INSERT OR IGNORE INTO mind_docs(message_id,owner) VALUES(?,?)", (message_id, owner))
        if not cur.rowcount:
            return False
        tokens = extract_words(subject + " " + body)
        counts = Counter(tokens)
        for word, freq in counts.items():
            ident = word_identity(word)
            self.conn.execute("""INSERT INTO mind_words(owner,word,length,signature,observed)
              VALUES(?,?,?,?,?) ON CONFLICT(owner,word) DO UPDATE SET observed=observed+excluded.observed""",
                              (owner, word, ident["length"], ident["signature"], freq))
            self.conn.execute("INSERT INTO mind_document_words VALUES(?,?,?,?)",
                              (owner,message_id,word,freq))
        # Context links connect observed nearby words; they accumulate with evidence.
        context = [w for w in tokens if w not in STOP_WORDS][:MAX_CONTEXT_WORDS]
        weights = defaultdict(int)
        for i, word in enumerate(context):
            for other in context[i+1:i+1+WINDOW]:
                if word == other:
                    continue
                weights[(word,other)] += 1
                weights[(other,word)] += 1
        for (word,other), weight in weights.items():
            self.conn.execute("""INSERT INTO mind_context(owner,source,target,weight) VALUES(?,?,?,?)
              ON CONFLICT(owner,source,target) DO UPDATE SET weight=weight+excluded.weight""",
                              (owner,word,other,weight))
        return True

    def reindex_legacy(self):
        """Index pre-existing mail without changing/deleting the original messages."""
        rows = self.conn.execute("""SELECT id,owner,subject,body FROM messages
          WHERE NOT EXISTS (SELECT 1 FROM mind_docs WHERE mind_docs.message_id=messages.id)""").fetchall()
        with self.conn:
            for row in rows:
                self.index_mail(row["owner"], row["id"], row["subject"], row["body"])
        return len(rows)

    def discover(self, owner: str, value: str, limit: int = 12) -> dict:
        """Discover relations with inspectable reasons, not assumed semantic equivalence."""
        src = word_identity(value)
        word, length, signature = src["word"], src["length"], src["signature"]
        limit = min(max(int(limit), 1), 30)
        candidates = {}

        def add(other, relation, points, evidence=0):
            if other == word:
                return
            item = candidates.setdefault(other, {"word": other,"score": 0.0,"reasons": [],"evidence": 0})
            item["score"] += points
            item["reasons"].append(relation)
            item["evidence"] = max(item["evidence"], evidence)

        for row in self.conn.execute("""SELECT word,observed,signature FROM mind_words
          WHERE owner=? AND length=? AND word<>? ORDER BY observed DESC, word LIMIT 150""",
                                      (owner,length,word)):
            add(row["word"],"same letter count: "+str(length),1.0, row["observed"])
            if row["signature"] == signature:
                add(row["word"],"same letters, different order",3.0,row["observed"])
        # Same-signature may be underrepresented by length query cap; include all top matches.
        for row in self.conn.execute("""SELECT word,observed FROM mind_words
          WHERE owner=? AND signature=? AND word<>? ORDER BY observed DESC LIMIT 100""",
                                     (owner,signature,word)):
            if row["word"] not in candidates:
                add(row["word"],"same letters, different order",4.0,row["observed"])
        for row in self.conn.execute("""SELECT target,weight FROM mind_context
          WHERE owner=? AND source=? ORDER BY weight DESC LIMIT 120""", (owner,word)):
            add(row["target"],"appeared nearby in messages",min(row["weight"],12)*1.25,row["weight"])
        for row in self.conn.execute("SELECT target,preference FROM mind_feedback WHERE owner=? AND source=?",(owner,word)):
            if row["target"] in candidates:
                candidates[row["target"]]["score"] += 8 * row["preference"]
                candidates[row["target"]]["reasons"].append("your feedback: "+("useful" if row["preference"]>0 else "not useful"))
        ordered = sorted(candidates.values(),key=lambda c:(-c["score"],-c["evidence"],c["word"]))[:limit]
        # Messages contain the query token (not merely substring) and belong to the authenticated owner.
        rows = self.conn.execute("""SELECT m.id,m.subject,m.folder,m.sender,m.created
          FROM mind_document_words AS dw JOIN messages AS m ON m.id=dw.message_id
          WHERE dw.owner=? AND dw.word=? AND m.owner=?
          ORDER BY m.created DESC LIMIT 20""",(owner,word,owner)).fetchall()
        return {**src, "chain": word_chain(word), "related": ordered,
                "messages": [dict(r) for r in rows],
                "method": "observed co-occurrence + same-length/same-letters + your feedback"}

    def feedback(self, owner: str, source: str, target: str, positive: bool):
        source = normalize_word(source)
        target = normalize_word(target)
        if source == target:
            raise ValueError("A word cannot rate itself")
        # Only let owners train on words actually present in their own mail data.
        rows = self.conn.execute("SELECT word FROM mind_words WHERE owner=? AND word IN (?,?)",(owner,source,target)).fetchall()
        if {r["word"] for r in rows} != {source,target}:
            raise ValueError("both words must be present in your mailbox")
        self.conn.execute("""INSERT INTO mind_feedback(owner,source,target,preference) VALUES(?,?,?,?)
          ON CONFLICT(owner,source,target) DO UPDATE SET preference=excluded.preference""",
                          (owner,source,target,1 if positive else -1))
        return True
