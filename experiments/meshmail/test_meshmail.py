"""End-to-end localhost tests for SLICKK Mesh Mail without network providers."""
import http.client
import hashlib
import hmac
import json
import time
from http.server import ThreadingHTTPServer
import os
from pathlib import Path
import socket
import tempfile
import threading
import unittest
from urllib.parse import urlencode

from meshmail import Node, authenticate, create_user, handler_factory, normalize_address

KEY=b'slickk-test-key-only-for-automated-tests-12345'


class LocalMeshTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.a=Node(str(Path(self.tmp.name)/'alpha.db'),'alpha.local',KEY)
        self.b=Node(str(Path(self.tmp.name)/'beta.db'),'beta.local',KEY)
        create_user(self.a.conn,'alice','correct-horse-staple-'+str(self.id()))
        create_user(self.b.conn,'bob','correct-horse-staple-'+str(self.id()))
        create_user(self.a.conn,'charlie','correct-horse-staple-'+str(self.id()))
        self.serve_a=ThreadingHTTPServer(('127.0.0.1',0),handler_factory(self.a))
        self.serve_b=ThreadingHTTPServer(('127.0.0.1',0),handler_factory(self.b))
        self.threads=[]
        for server in (self.serve_a,self.serve_b):
            t=threading.Thread(target=server.serve_forever,daemon=True)
            t.start();self.threads.append(t)
        self.a.peers['beta.local']=f'http://127.0.0.1:{self.serve_b.server_port}'

    def tearDown(self):
        for server in (self.serve_a,self.serve_b):server.shutdown();server.server_close()
        for t in self.threads:t.join(3)
        self.a.close();self.b.close()
        self.tmp.cleanup()

    def test_user_password_authentication(self):
        self.assertTrue(authenticate(self.a.conn,'alice','correct-horse-staple-'+str(self.id())))
        self.assertFalse(authenticate(self.a.conn,'alice','wrong-password'))
        self.assertFalse(authenticate(self.a.conn,'unknown','random-password'))

    def test_local_two_user_delivery_and_search(self):
        self.a.deliver('alice','charlie@alpha.local','Test subject','Hello, Charlie')
        inbox=self.a.messages('charlie')
        self.assertEqual(len(inbox),1)
        self.assertEqual(inbox[0]['sender'],'alice@alpha.local')
        self.assertEqual(self.a.messages('charlie','inbox','subject')[0]['body'],'Hello, Charlie')
        self.assertEqual(len(self.a.messages('alice','sent')),1)

    def test_replay_signature_rejected(self):
        from uuid import uuid4
        mid = str(uuid4())
        mail = {'id': mid, 'from': 'alice@alpha.local', 'to': 'bob@beta.local',
                'subject': 'Replay test', 'body': 'Delivered once', 'sent_at': int(time.time())}
        payload = json.dumps(mail).encode()
        stamp, nonce = str(int(time.time())), 'a'*32
        signature = hmac.new(KEY, f'{stamp}.{nonce}.'.encode()+payload, hashlib.sha256).hexdigest()
        self.assertEqual(self.b.receive(payload, stamp, nonce, signature),mid)
        with self.assertRaisesRegex(PermissionError,'replayed'):
            self.b.receive(payload, stamp, nonce, signature)
        self.assertEqual(len(self.b.messages('bob')),1)

    def test_unknown_route_rejected(self):
        with self.assertRaisesRegex(ValueError,'trusted route'):
            self.a.deliver('alice','somebody@unknown.invalid','Hi','Hi')

    def test_remote_node_delivery_acks_and_deduplicates(self):
        mid=self.a.deliver('alice','bob@beta.local','Across nodes','Independent mail protocol demo')
        self.assertEqual(len(self.b.messages('bob')),1)
        self.assertEqual(self.b.messages('bob')[0]['global_id'],mid)
        self.assertEqual(self.a.conn.execute('select count(*) from queued').fetchone()[0],0)

    def test_failed_delivery_queues_and_can_retry(self):
        self.a.peers['beta.local']='http://127.0.0.1:1'
        self.a.deliver('alice','bob@beta.local','Queue proof','Stored while offline')
        self.assertEqual(self.a.conn.execute('select count(*) from queued').fetchone()[0],1)
        self.assertEqual(len(self.b.messages('bob')),0)
        self.a.peers['beta.local']=f'http://127.0.0.1:{self.serve_b.server_port}'
        self.assertEqual(self.a.retry(),1)
        self.assertEqual(len(self.b.messages('bob')),1)
        self.assertEqual(self.a.conn.execute('select count(*) from queued').fetchone()[0],0)

    def test_invalid_signature_is_rejected(self):
        conn=http.client.HTTPConnection('127.0.0.1',self.serve_b.server_port,timeout=4)
        conn.request('POST','/mesh/v1/receive',body=b'{}',headers={'X-Slickk-Time':'1',
            'X-Slickk-Nonce':'0'*32,'X-Slickk-Signature':'invalid'})
        res=conn.getresponse();self.assertEqual(res.status,403);res.read();conn.close()

    def test_login_and_csrf(self):
        conn=http.client.HTTPConnection('127.0.0.1',self.serve_a.server_port,timeout=4)
        data=urlencode({'name':'alice','password':'correct-horse-staple-'+str(self.id())})
        conn.request('POST','/login',data,{'Content-Type':'application/x-www-form-urlencoded'})
        res=conn.getresponse()
        self.assertEqual(res.status,303)
        cookie=res.getheader('Set-Cookie').split(';')[0]
        res.read()
        conn.request('POST','/send',urlencode({'to':'charlie@alpha.local','subject':'X','body':'Y'}),
                     {'Cookie':cookie})
        res=conn.getresponse();self.assertEqual(res.status,403);res.read()
        conn.request('GET','/',headers={'Cookie':cookie})
        res=conn.getresponse();self.assertEqual(res.status,200)
        body=res.read().decode()
        self.assertIn('Signed in:',body)
        self.assertIn('csrf',body)
        conn.close()

    def test_data_persists_across_connection_close(self):
        self.a.deliver('alice','charlie@alpha.local','Persistent','Written to disk')
        import sqlite3
        c=sqlite3.connect(self.a.db_path)
        self.assertEqual(c.execute("select count(*) from messages where owner='charlie'").fetchone()[0],1)
        c.close()

    def test_no_script_injection_in_subject(self):
        self.a.deliver('alice','charlie@alpha.local','<script>alert(1)</script>','<img onerror="oops">')
        data=self.a.messages('charlie')[0]
        self.assertEqual(data['subject'],'<script>alert(1)</script>')
        conn=http.client.HTTPConnection('127.0.0.1',self.serve_a.server_port,timeout=4)
        conn.request('POST','/login',urlencode({'name':'charlie','password':'correct-horse-staple-'+str(self.id())}))
        res=conn.getresponse();cookie=res.getheader('Set-Cookie').split(';')[0];res.read()
        conn.request('GET','/',headers={'Cookie':cookie})
        res=conn.getresponse();text=res.read().decode()
        self.assertNotIn('<script>alert(1)</script>',text)
        self.assertIn('&lt;script&gt;',text)
        conn.close()


if __name__=='__main__':unittest.main()
