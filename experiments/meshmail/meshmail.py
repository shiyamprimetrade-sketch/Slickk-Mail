"""SLICKK Mesh Mail prototype: standard-library, authenticated local mailbox nodes.

Not SMTP, Gmail compatible, end-to-end encrypted, or suitable for deployment on the
public Internet. Mesh transport uses authenticated HTTP for controlled LAN labs.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from getpass import getpass
import hashlib
import hmac
from html import escape
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import re
import secrets
import sqlite3
import threading
import time
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, urlopen
from uuid import uuid4

MAX_REQUEST = 72_000
CLOCK_SKEW = 300
USER_RE = re.compile(r"^[a-z][a-z0-9_.-]{1,31}$")
NODE_RE = re.compile(r"^[a-z0-9][a-z0-9.-]{0,126}$")


def now() -> int:
    return int(time.time())


def connect(db_path):
    c = sqlite3.connect(db_path, timeout=20, check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA busy_timeout=20000")
    c.execute("PRAGMA journal_mode=WAL")
    c.executescript("""
      CREATE TABLE IF NOT EXISTS users (name TEXT PRIMARY KEY, salt BLOB NOT NULL,
        hash BLOB NOT NULL);
      CREATE TABLE IF NOT EXISTS messages (id TEXT PRIMARY KEY, global_id TEXT NOT NULL,
        owner TEXT NOT NULL, folder TEXT NOT NULL, sender TEXT NOT NULL,
        recipient TEXT NOT NULL, subject TEXT NOT NULL, body TEXT NOT NULL,
        created INTEGER NOT NULL);
      CREATE INDEX IF NOT EXISTS idx_mail ON messages(owner,folder,created DESC);
      CREATE UNIQUE INDEX IF NOT EXISTS idx_dedupe ON messages(owner,folder,global_id);
      CREATE TABLE IF NOT EXISTS queued (global_id TEXT PRIMARY KEY,
        payload TEXT NOT NULL, domain TEXT NOT NULL, created INTEGER NOT NULL,
        attempts INTEGER NOT NULL DEFAULT 0, last_error TEXT NOT NULL DEFAULT '');
      CREATE TABLE IF NOT EXISTS nonces (nonce TEXT PRIMARY KEY, created INTEGER NOT NULL);
    """)
    c.commit()
    return c


def passhash(password, salt):
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)


def create_user(conn, name, password):
    if not USER_RE.fullmatch(name):
        raise ValueError("username: 2-32 lowercase characters, numbers, _.-")
    if len(password) < 12:
        raise ValueError("minimum password length is 12")
    salt = os.urandom(16)
    with conn:
        conn.execute("INSERT INTO users(name,salt,hash) VALUES(?,?,?)",
                     (name, salt, passhash(password, salt)))


def authenticate(conn, name, password):
    row = conn.execute("SELECT salt,hash FROM users WHERE name=?", (name,)).fetchone()
    if not row:
        # Timing resistance for unknown users
        passhash(password, b"\0" * 16)
        return False
    return hmac.compare_digest(passhash(password, row["salt"]), row["hash"])


def normalize_address(address):
    value = address.strip().lower()
    if value.count("@") != 1:
        raise ValueError("recipient must be user@node")
    user, domain = value.split("@")
    if not USER_RE.fullmatch(user) or not NODE_RE.fullmatch(domain):
        raise ValueError("invalid mailbox address")
    return user, domain


def store_mail(conn, owner, folder, mail):
    conn.execute("""INSERT OR IGNORE INTO messages
      (id,global_id,owner,folder,sender,recipient,subject,body,created)
      VALUES(?,?,?,?,?,?,?,?,?)""", (str(uuid4()), mail["id"], owner, folder,
            mail["from"], mail["to"], mail["subject"], mail["body"], mail["sent_at"]))


class Node:
    def __init__(self, db_path, node_name, shared_key, peers=None):
        if not NODE_RE.fullmatch(node_name):
            raise ValueError("invalid node name")
        self.db_path, self.name, self.key = db_path, node_name, shared_key
        self.peers = peers or {}
        self.lock = threading.RLock()
        self.sessions = {}  # volatile; logout on restart is intentional
        self.conn = connect(db_path)

    def close(self):
        self.conn.close()

    def deliver(self, sender, recipient, subject, body):
        user, domain = normalize_address(recipient)
        if not USER_RE.fullmatch(sender):
            raise ValueError("invalid sender")
        if not 0 < len(subject) <= 200 or len(body.encode()) > 60_000:
            raise ValueError("subject required (<=200); body max 60KB")
        mail = {"id": str(uuid4()), "from": f"{sender}@{self.name}",
                "to": f"{user}@{domain}", "subject": subject,
                "body": body, "sent_at": now()}
        with self.lock, self.conn:
            if not self.conn.execute("SELECT 1 FROM users WHERE name=?", (sender,)).fetchone():
                raise ValueError("unknown sender")
            if domain == self.name:
                if not self.conn.execute("SELECT 1 FROM users WHERE name=?", (user,)).fetchone():
                    raise ValueError("recipient not found")
                store_mail(self.conn, user, "inbox", mail)
            elif domain not in self.peers:
                raise ValueError("no trusted route to node")
            else:
                self.conn.execute("INSERT INTO queued(global_id,payload,domain,created) VALUES(?,?,?,?)",
                                  (mail["id"], json.dumps(mail), domain, now()))
            store_mail(self.conn, sender, "sent", mail)
        if domain != self.name:
            self.retry()
        return mail["id"]

    def receive(self, payload, stamp, nonce, signature):
        if not self.key:
            raise PermissionError("inter-node transport is disabled")
        if abs(now() - int(stamp)) > CLOCK_SKEW:
            raise PermissionError("expired message")
        if not re.fullmatch(r"[a-f0-9]{32}", nonce):
            raise PermissionError("bad nonce")
        raw = f"{stamp}.{nonce}.".encode() + payload
        expected = hmac.new(self.key, raw, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise PermissionError("untrusted peer")
        mail = json.loads(payload)
        if set(mail) != {"id", "from", "to", "subject", "body", "sent_at"}:
            raise ValueError("invalid fields")
        if not isinstance(mail["id"], str) or len(mail["id"]) > 64:
            raise ValueError("invalid message ID")
        name, node = normalize_address(mail["to"])
        normalize_address(mail["from"])
        if node != self.name or not isinstance(mail["body"], str) or len(mail["body"].encode()) > 60_000:
            raise ValueError("wrong destination or size")
        if not isinstance(mail["subject"], str) or len(mail["subject"]) > 200:
            raise ValueError("invalid subject")
        if not isinstance(mail["sent_at"], int):
            raise ValueError("bad time")
        with self.lock, self.conn:
            self.conn.execute("DELETE FROM nonces WHERE created < ?", (now()-CLOCK_SKEW,))
            try:
                self.conn.execute("INSERT INTO nonces(nonce,created) VALUES(?,?)", (nonce,now()))
            except sqlite3.IntegrityError as exc:
                raise PermissionError("replayed request") from exc
            if not self.conn.execute("SELECT 1 FROM users WHERE name=?", (name,)).fetchone():
                raise ValueError("recipient not found")
            store_mail(self.conn, name, "inbox", mail)
        return mail["id"]

    def retry(self):
        if not self.key:
            return 0
        with self.lock:
            rows = list(self.conn.execute("SELECT * FROM queued ORDER BY created LIMIT 100"))
        delivered = 0
        for row in rows:
            dest = self.peers.get(row["domain"])
            if not dest:
                continue
            stamp, nonce = str(now()), secrets.token_hex(16)
            payload = row["payload"].encode()
            signature = hmac.new(self.key, f"{stamp}.{nonce}.".encode()+payload, hashlib.sha256).hexdigest()
            req = Request(dest.rstrip("/")+"/mesh/v1/receive", data=payload, method="POST",
                          headers={"Content-Type":"application/json", "X-Slickk-Time":stamp,
                                   "X-Slickk-Nonce":nonce,"X-Slickk-Signature":signature})
            try:
                with urlopen(req, timeout=3) as resp:
                    if resp.status != 200:
                        raise OSError("peer did not acknowledge")
                with self.lock, self.conn:
                    self.conn.execute("DELETE FROM queued WHERE global_id=?", (row["global_id"],))
                delivered += 1
            except Exception as exc:
                with self.lock, self.conn:
                    self.conn.execute("UPDATE queued SET attempts=attempts+1,last_error=? WHERE global_id=?",
                                      (str(exc)[:200],row["global_id"]))
        return delivered

    def messages(self, owner, folder="inbox", query=""):
        if folder not in ("inbox", "sent"):
            raise ValueError("invalid folder")
        pattern = "%" + query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        with self.lock:
            return list(self.conn.execute("""SELECT * FROM messages WHERE owner=? AND folder=?
              AND (subject LIKE ? ESCAPE '\\' OR sender LIKE ? ESCAPE '\\'
                   OR body LIKE ? ESCAPE '\\')
              ORDER BY created DESC LIMIT 100""", (owner, folder, pattern, pattern, pattern)))


def handler_factory(node):
    class Handler(BaseHTTPRequestHandler):
        server_version = "SlickkMeshMail/0.1"
        def log_message(self, *args):
            return

        def reply(self, code, content, content_type="text/html; charset=utf-8", headers=None):
            if isinstance(content, str):
                content = content.encode()
            self.send_response(code)
            self.send_header("Content-Type",content_type)
            self.send_header("Content-Length",str(len(content)))
            self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Cache-Control","no-store")
            self.send_header("Content-Security-Policy","default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'")
            for k,v in (headers or {}).items():self.send_header(k,v)
            self.end_headers()
            self.wfile.write(content)

        def session(self):
            cookie=SimpleCookie()
            try:cookie.load(self.headers.get("Cookie",""))
            except Exception:return None
            tok=cookie.get("sid")
            if tok:
                with node.lock:
                    value=node.sessions.get(tok.value)
                    if value and value[1]>now():return value
            return None

        def page(self, content, title="SLICKK Mesh Mail"):
            return ("<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'>"
             "<meta charset='utf-8'><title>"+escape(title)+"</title><style>body{font:16px system-ui;margin:2rem auto;max-width:780px;padding:0 1rem;background:#101827;color:#f1f5f9}"
             "a{color:#22d3ee}input,textarea,button{padding:9px;margin:4px 0;box-sizing:border-box;width:100%;max-width:100%;border-radius:5px}"
             "section,article{border:1px solid #435267;padding:12px;margin:10px 0;border-radius:7px}textarea{min-height:100px}</style></head><body><h1>SLICKK Mesh Mail</h1>"
             +content+"</body></html>")

        def do_GET(self):
            parts=urlsplit(self.path)
            if parts.path=="/healthz":
                self.reply(200,json.dumps({"status":"ok","node":node.name}).encode(),"application/json")
                return
            sess=self.session()
            if not sess:
                self.reply(200,self.page("<p>Controlled network proof-of-concept. Not public email.</p>"
                    "<form method='post' action='/login'><input name='name' placeholder='Username' required>"
                    "<input type='password' name='password' placeholder='Password' required>"
                    "<button>Sign in</button></form>"))
                return
            username, _, csrf=sess
            args=parse_qs(parts.query)
            folder=args.get("folder",["inbox"])[0]
            if folder not in ("inbox","sent"):folder="inbox"
            q=args.get("q",[""])[0][:100]
            with node.lock:
                rows=node.messages(username,folder,q)
                pending=node.conn.execute("SELECT COUNT(*) FROM queued").fetchone()[0]
            t="<p>Signed in: <strong>"+escape(username+"@"+node.name)+"</strong></p>"
            t+="<nav><a href='/?folder=inbox'>Inbox</a> | <a href='/?folder=sent'>Sent</a> | Pending transfers: "+str(pending)+"</nav>"
            t+="<form method='get'><input name='q' placeholder='Search' value='"+escape(q,quote=True)+"'><button>Search</button></form>"
            t+="<section><h2>Compose</h2><form method='post' action='/send'><input type='hidden' name='csrf' value='"+csrf+"'>"
            t+="<input name='to' placeholder='recipient@node' required maxlength=160><input name='subject' placeholder='Subject' required maxlength=200>"
            t+="<textarea name='body' required maxlength=60000></textarea><button>Send (or queue)</button></form></section>"
            t+="<form method='post' action='/retry'><input type='hidden' name='csrf' value='"+csrf+"'><button>Retry queued transfers</button></form>"
            t+="<form method='post' action='/logout'><input type='hidden' name='csrf' value='"+csrf+"'><button>Sign out</button></form>"
            t+="<h2>"+escape(folder.title())+"</h2>"
            for m in rows:
                t+="<article><b>"+escape(m['subject'])+"</b><p>From: "+escape(m['sender'])+"<br>To: "+escape(m['recipient'])+"</p>"
                t+="<pre style='white-space:pre-wrap;word-break:break-word'>"+escape(m['body'])+"</pre></article>"
            self.reply(200,self.page(t))

        def do_POST(self):
            size=self.headers.get("Content-Length","")
            if not size.isdigit() or int(size)>MAX_REQUEST:
                self.reply(413,"Payload too large")
                return
            raw=self.rfile.read(int(size))
            if self.path=="/mesh/v1/receive":
                try:
                    mid=node.receive(raw,self.headers.get('X-Slickk-Time',''),
                                     self.headers.get('X-Slickk-Nonce',''),self.headers.get('X-Slickk-Signature',''))
                    self.reply(200,json.dumps({"id":mid}),"application/json")
                except PermissionError:self.reply(403,"unauthorized")
                except (ValueError,TypeError,KeyError,json.JSONDecodeError):self.reply(400,"invalid message")
                return
            try:
                form={k:v[0] for k,v in parse_qs(raw.decode(),keep_blank_values=True).items()}
            except UnicodeDecodeError:
                self.reply(400,"invalid form")
                return
            if self.path=="/login":
                with node.lock:
                    ok=authenticate(node.conn,form.get('name',''),form.get('password',''))
                if not ok:
                    self.reply(401,"Invalid credentials")
                    return
                tok=secrets.token_urlsafe(32)
                with node.lock:node.sessions[tok]=(form['name'],now()+12*3600,secrets.token_urlsafe(24))
                self.reply(303,b"",headers={"Location":"/","Set-Cookie":f"sid={tok}; HttpOnly; SameSite=Lax; Path=/"})
                return
            sess=self.session()
            if not sess or not hmac.compare_digest(sess[2],form.get("csrf","")):
                self.reply(403,"Login or CSRF token required")
                return
            if self.path=="/logout":
                cookie=SimpleCookie()
                cookie.load(self.headers.get('Cookie',''))
                token=cookie.get('sid')
                if token:
                    with node.lock:node.sessions.pop(token.value,None)
                self.reply(303,b"",headers={"Location":"/","Set-Cookie":"sid=; Max-Age=0; Path=/"})
                return
            if self.path=="/send":
                try:
                    node.deliver(sess[0],form.get('to',''),form.get('subject',''),form.get('body',''))
                except ValueError as exc:
                    self.reply(400,self.page("<p>"+escape(str(exc))+"</p><a href='/'>Back</a>"))
                    return
            elif self.path=="/retry":node.retry()
            else:
                self.reply(404,"Not found")
                return
            self.reply(303,b"",headers={"Location":"/"})
    return Handler


def serve(node, host, port):
    server=ThreadingHTTPServer((host,port),handler_factory(node))
    print(f"SLICKK Mesh Mail {node.name}: http://{host}:{server.server_port}",flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close();node.close()


def main():
    p=argparse.ArgumentParser(description="SLICKK Mesh Mail local network experiment")
    p.add_argument("action",choices=["serve","create-user","retry"])
    p.add_argument("--db",default="meshmail.db")
    p.add_argument("--node",required=True)
    p.add_argument("--host",default="127.0.0.1")
    p.add_argument("--port",type=int,default=8097)
    p.add_argument("--name",help="admin-created local user")
    p.add_argument("--peers",help="JSON file containing trusted node names and reachable URLs")
    a=p.parse_args()
    peers=json.load(open(a.peers,encoding="utf-8")) if a.peers else {}
    if not isinstance(peers,dict) or any(not NODE_RE.fullmatch(k) or not isinstance(v,str) or
       (not v.startswith('http://127.0.0.1:') and not v.startswith('http://localhost:')) for k,v in peers.items()):
        p.error("v0.1 only permits explicit localhost peers; do not expose unauthenticated HTTP publicly")
    secret=os.getenv("SLICKK_MESH_KEY","").encode()
    if secret and len(secret)<32:p.error("SLICKK_MESH_KEY must be at least 32 bytes")
    node=Node(a.db,a.node,secret,peers)
    if a.action=="serve":
        if a.host not in ("127.0.0.1","::1"):
            p.error("v0.1 binds only to loopback; public exposure is not supported")
        serve(node,a.host,a.port)
    elif a.action=="create-user":
        if not a.name:p.error("--name required")
        one=getpass("Password (at least 12 characters): ")
        two=getpass("Repeat password: ")
        if one!=two:p.error("passwords do not match")
        create_user(node.conn,a.name,one)
        print(f"Created local user {a.name}@{a.node}")
        node.close()
    else:
        print(f"Delivered {node.retry()} queued messages")
        node.close()


if __name__=="__main__":main()
