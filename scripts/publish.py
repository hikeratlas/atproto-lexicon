#!/usr/bin/env python3
"""Publishes the lexicons into Hiker Atlas's own AT Protocol account
(@hikeratlas.com), as com.atproto.lexicon.schema records keyed by NSID, so
anyone can resolve them: DNS TXT _lexicon.<authority> -> this DID -> the
record. Run by .github/workflows/publish.yml on merges to main.

    BSKY_APP_PASSWORD=... python3 scripts/publish.py
    python3 scripts/publish.py --dry-run     # what would change; no password

Only changed schemas are written. A lexicon removed from this repository is
left published (records in people's accounts may still use it).
"""
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

DID = 'did:plc:7onixtzlmdjijmp7ympxedte'  # @hikeratlas.com
COLLECTION = 'com.atproto.lexicon.schema'
ROOT = pathlib.Path(__file__).resolve().parent.parent / 'lexicons'


def call(url, body=None, token=None):
    req = urllib.request.Request(url, data=None if body is None else json.dumps(body).encode(),
                                 headers={'content-type': 'application/json', 'user-agent': 'hikeratlas-lexicon-publish'})
    if token:
        req.add_header('authorization', f'Bearer {token}')
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code in (400, 404) and body is None:
            return None  # not there (getRecord)
        raise SystemExit(f'{url.split("?")[0]}: HTTP {e.code} {e.read().decode(errors="replace")[:300]}')


def pds_of(did):
    doc = call(f'https://plc.directory/{did}')
    return next(s['serviceEndpoint'] for s in doc['service'] if s['id'] == '#atproto_pds')


def main():
    dry = '--dry-run' in sys.argv
    pds = pds_of(DID)
    lexicons = {}
    for p in sorted(ROOT.rglob('*.json')):
        d = json.loads(p.read_text())
        lexicons[d['id']] = d
    token = None
    if not dry:
        password = os.environ.get('BSKY_APP_PASSWORD')
        if not password:
            raise SystemExit('BSKY_APP_PASSWORD is not set')
        token = call(f'{pds}/xrpc/com.atproto.server.createSession', {'identifier': DID, 'password': password})['accessJwt']
    changed = 0
    for nsid, doc in lexicons.items():
        record = {'$type': COLLECTION, **doc}
        have = call(f'{pds}/xrpc/com.atproto.repo.getRecord?repo={DID}&collection={COLLECTION}&rkey={nsid}')
        if have and have.get('value') == record:
            print(f'  {nsid}: unchanged')
            continue
        changed += 1
        if dry:
            print(f'  {nsid}: would {"update" if have else "publish"}')
            continue
        call(f'{pds}/xrpc/com.atproto.repo.putRecord',
             {'repo': DID, 'collection': COLLECTION, 'rkey': nsid, 'record': record}, token)
        print(f'  {nsid}: {"updated" if have else "published"}')
    print(f'{changed} of {len(lexicons)} lexicons {"to publish" if dry else "published"} (at://{DID}/{COLLECTION}/...)')


if __name__ == '__main__':
    main()
