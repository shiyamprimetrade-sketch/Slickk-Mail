"""Run two temporary, authenticated mailbox nodes on one Windows/Linux computer.

The demonstration never opens a public port. Data is deleted at exit.
"""
import atexit
from http.server import ThreadingHTTPServer
from pathlib import Path
import secrets
import tempfile
import threading

from meshmail import Node, create_user, handler_factory


def main():
    work = tempfile.TemporaryDirectory(prefix='slickk-mesh-demo-')
    atexit.register(work.cleanup)
    key = secrets.token_bytes(32)
    alpha = Node(str(Path(work.name) / 'alpha.db'), 'alpha.local', key)
    beta = Node(str(Path(work.name) / 'beta.db'), 'beta.local', key)
    pa, pb = secrets.token_urlsafe(18), secrets.token_urlsafe(18)
    create_user(alpha.conn, 'alice', pa)
    create_user(beta.conn, 'bob', pb)
    servers = [ThreadingHTTPServer(('127.0.0.1', 8097), handler_factory(alpha)),
               ThreadingHTTPServer(('127.0.0.1', 8098), handler_factory(beta))]
    alpha.peers['beta.local'] = 'http://127.0.0.1:8098'
    beta.peers['alpha.local'] = 'http://127.0.0.1:8097'
    threads=[]
    for s in servers:
        t=threading.Thread(target=s.serve_forever,daemon=True)
        t.start();threads.append(t)
    print('\nSLICKK Mesh Mail: independent, two-node localhost demonstration\n', flush=True)
    print(f'Node 1: http://127.0.0.1:8097  login alice / {pa}')
    print(f'Node 2: http://127.0.0.1:8098  login bob   / {pb}')
    print('Send from alice to bob@beta.local and from bob to alice@alpha.local.')
    print('Test-only passwords appear on this private terminal; do not share them.')
    print('Data is temporary; Ctrl+C ends both services and deletes the databases.\n')
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print('\nStopping demonstration...')
    finally:
        for s in servers:s.shutdown();s.server_close()
        for t in threads:t.join(4)
        alpha.close();beta.close()
        work.cleanup()


if __name__ == '__main__':
    main()
