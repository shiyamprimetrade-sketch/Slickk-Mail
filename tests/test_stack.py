"""STATIC-only checks. These tests do NOT claim Docker, Windows, mail or DNS work."""
from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_compose(name):
    return yaml.safe_load((ROOT / 'compose' / name).read_text(encoding='utf-8'))


def test_compose_is_parseable_and_has_stalwart_bulwark():
    for name in ('local.yaml', 'production.yaml'):
        doc = load_compose(name)
        assert set(doc['services']) == {'stalwart', 'bulwark'}
        assert 'volumes' in doc


def test_local_ports_loopback_only():
    for service in load_compose('local.yaml')['services'].values():
        assert all(str(port).startswith('127.0.0.1:') for port in service.get('ports', []))


def test_production_bootstrap_and_webmail_not_public():
    s = load_compose('production.yaml')['services']
    assert '127.0.0.1:8080:8080' in s['stalwart']['ports']
    assert '127.0.0.1:3000:3000' in s['bulwark']['ports']


def test_persistent_mail_volumes_and_nonfloating_major_tags():
    for name in ('local.yaml', 'production.yaml'):
        doc = load_compose(name)
        for component in ('stalwart-etc', 'stalwart-data', 'bulwark-data'):
            assert component in doc['volumes']
        for svc in doc['services'].values():
            assert ':latest' not in svc['image']
            assert svc['restart'] == 'unless-stopped'


def test_never_commit_secrets_to_configuration():
    for f in [ROOT / 'compose' / 'local.yaml', ROOT / 'compose' / 'production.yaml']:
        s = f.read_text(encoding='utf-8')
        assert not re.search(r'eyJhIjoi[A-Za-z0-9._-]{30,}', s), 'Tunnel token leaked'
        assert 'password:' not in s.lower()


def test_docs_and_codex_prompt_present():
    for name in ('AGENTS.md','README.md','CODEX_MASTER_PROMPT.md',
                 'docs/WINDOWS.md','docs/DNS.md','docs/SELF-HOSTING.md',
                 'docs/ACCEPTANCE.md','docs/SECURITY.md'):
        assert (ROOT/name).is_file(), name
