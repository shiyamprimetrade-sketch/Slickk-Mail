"""Tests for explainable, per-user SLICKK WordMind learning."""
import http.client
from http.server import ThreadingHTTPServer
from pathlib import Path
import re
import tempfile
import threading
import unittest
from urllib.parse import urlencode

from meshmail import Node, create_user, handler_factory
from wordmind import count_word, word_chain, word_identity, normalize_word, MAX_DOCUMENT_WORDS


class WordMindUnitTests(unittest.TestCase):
    def test_letters_count_one_and_word_chain(self):
        x = word_identity("ABCA")
        self.assertEqual(x["letters"], ["A", "B", "C", "A"])
        self.assertEqual(x["length"], 4)
        self.assertEqual(x["number_word"], "FOUR")
        self.assertEqual(word_chain("ABCA"), ["ABCA", "FOUR"])
        self.assertEqual(word_chain("APPLE"), ["APPLE", "FIVE", "FOUR"])
        self.assertEqual(word_chain("FOUR"), ["FOUR"])

    def test_count_word_and_input_validation(self):
        self.assertEqual(count_word(21), "TWENTY ONE")
        self.assertEqual(count_word(100), "ONE HUNDRED")
        self.assertEqual(count_word(9999), "NINE THOUSAND NINE HUNDRED NINETY NINE")
        for val in (-1, 10000, True):
            with self.subTest(val=val), self.assertRaises(ValueError):count_word(val)
        for val in ("", "a<script>", "word space", "a" * 40, "école"):
            with self.subTest(val=val), self.assertRaises(ValueError):normalize_word(val)


class WordMindMailboxTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "mail.db")
        self.node = Node(self.db,"alpha.local",b"private-local-test-key-32-bytes-long!!!")
        create_user(self.node.conn,"alice","super-secret-long-password-123")
        create_user(self.node.conn,"bob","super-secret-long-password-456")

    def tearDown(self):
        self.node.close()
        self.tmp.cleanup()

    def test_interaction_discovers_relationships_and_explains_them(self):
        self.node.deliver("alice","bob@alpha.local","ABCA CABA","Constructive relationships")
        result = self.node.mind.discover("bob","abca")
        related = {r["word"]:r for r in result["related"]}
        self.assertIn("caba",related)
        self.assertIn("same letters, different order",related["caba"]["reasons"])
        self.assertIn("same letter count: 4",related["caba"]["reasons"])
        self.assertIn("appeared nearby in messages",related["caba"]["reasons"])
        self.assertEqual(result["chain"],["ABCA","FOUR"])
        self.assertEqual(result["messages"][0]["subject"],"ABCA CABA")

    def test_per_user_isolation_and_no_cross_user_learning(self):
        self.node.deliver("alice","bob@alpha.local","ABCA CABA", "bob private pattern")
        # Bob's inbox data is not visible to a third user.
        create_user(self.node.conn,"charlie","a-different-very-long-password")
        result = self.node.mind.discover("charlie","abca")
        self.assertEqual(result["related"],[])
        self.assertEqual(result["messages"],[])
        with self.assertRaisesRegex(ValueError,"both words"):
            self.node.mind.feedback("charlie","abca","caba",True)

    def test_user_feedback_changes_rank_and_is_reversible(self):
        self.node.deliver("alice","bob@alpha.local","ABCA CABA WXYZ", "Four letter symbols")
        before = {r["word"]: r["score"] for r in self.node.mind.discover("bob","abca")["related"]}
        with self.node.lock,self.node.conn:
            self.node.mind.feedback("bob","abca","caba",True)
        higher = {r["word"]: r["score"] for r in self.node.mind.discover("bob","abca")["related"]}
        self.assertGreater(higher["caba"],before["caba"])
        with self.node.lock,self.node.conn:
            self.node.mind.feedback("bob","abca","caba",False)
        lower = {r["word"]: r["score"] for r in self.node.mind.discover("bob","abca")["related"]}
        self.assertLess(lower["caba"],before["caba"])

    def test_rebuild_after_legacy_mail_and_reopen_is_idempotent(self):
        self.node.deliver("alice","bob@alpha.local","APPLE", "FIVE FOUR")
        m = self.node.messages("bob")[0]
        # Simulate legacy migration: wipe only derived tables, keep actual mail.
        with self.node.conn:
            for name in ("mind_docs","mind_words","mind_document_words","mind_context","mind_feedback"):
                self.node.conn.execute("DELETE FROM "+name)
        self.assertEqual(self.node.mind.reindex_legacy(),2) # inbox and sender's sent copy
        self.assertEqual(self.node.mind.reindex_legacy(),0)
        observed = self.node.conn.execute("SELECT observed FROM mind_words WHERE owner='bob' AND word='apple'").fetchone()[0]
        self.assertEqual(observed,1)
        self.node.close()
        self.node = Node(self.db,"alpha.local",b"private-local-test-key-32-bytes-long!!!")
        self.assertEqual(self.node.mind.reindex_legacy(),0)
        self.assertEqual(self.node.mind.discover("bob","apple")["messages"][0]["id"],m['id'])

    def test_bounded_index_even_for_long_body(self):
        body = " ".join([f"word{n}" for n in range(1000)])
        self.node.deliver("alice","bob@alpha.local","Limit test",body)
        counts=self.node.conn.execute("SELECT COUNT(*) FROM mind_document_words WHERE owner='bob'").fetchone()[0]
        self.assertLessEqual(counts, MAX_DOCUMENT_WORDS)

    def test_browser_requires_login_and_csrf_for_feedback(self):
        server = ThreadingHTTPServer(('127.0.0.1',0),handler_factory(self.node))
        runner = threading.Thread(target=server.serve_forever,daemon=True)
        runner.start()
        try:
            c = http.client.HTTPConnection('127.0.0.1',server.server_port, timeout=5)
            c.request('GET','/discover?word=abca')
            resp=c.getresponse(); page=resp.read().decode()
            self.assertEqual(resp.status,200)
            self.assertNotIn('Transformation chain:',page) # login first
            self.node.deliver("alice","bob@alpha.local","ABCA CABA", "Find the connection")
            c.request('POST','/login',urlencode({'name':'bob','password':'super-secret-long-password-456'}))
            resp=c.getresponse();self.assertEqual(resp.status,303)
            cookie=resp.getheader('Set-Cookie').split(';')[0];resp.read()
            c.request('GET','/discover?word=abca',headers={'Cookie':cookie})
            resp=c.getresponse();body=resp.read().decode()
            self.assertEqual(resp.status,200)
            self.assertIn('Transformation chain:',body)
            self.assertIn('ABCA → FOUR',body)
            c.request('POST','/feedback',urlencode({'word':'abca','related':'caba','vote':'yes'}),{'Cookie':cookie})
            resp=c.getresponse();self.assertEqual(resp.status,403);resp.read()
            csrf=re.search(r"name='csrf' value='([^']+)'",body).group(1)
            c.request('POST','/feedback',urlencode({'word':'abca','related':'caba','vote':'yes','csrf':csrf}),{'Cookie':cookie})
            resp=c.getresponse();self.assertEqual(resp.status,303);resp.read()
            c.close()
        finally:
            server.shutdown();server.server_close();runner.join(5)


if __name__ == '__main__': unittest.main()
