#!/usr/bin/env python3
"""Checks the lexicons: each file parses, its id matches its path, every ref
resolves to a lexicon here (or com.atproto.*), and the permission set names
only collections defined here."""
import json, pathlib, sys

root = pathlib.Path(__file__).resolve().parent.parent / 'lexicons'
docs, bad = {}, []
for p in sorted(root.rglob('*.json')):
    try:
        d = json.loads(p.read_text())
    except ValueError as e:
        bad.append(f'{p}: {e}'); continue
    want = '.'.join(p.relative_to(root).with_suffix('').parts)
    if d.get('id') != want: bad.append(f"{p}: id {d.get('id')!r}, expected {want!r}")
    if d.get('lexicon') != 1: bad.append(f'{p}: lexicon must be 1')
    docs[d.get('id')] = d

def refs(x):
    if isinstance(x, dict):
        if x.get('type') == 'ref': yield x['ref']
        for v in x.values(): yield from refs(v)
    elif isinstance(x, list):
        for v in x: yield from refs(v)

records = {i for i, d in docs.items() if d.get('defs', {}).get('main', {}).get('type') == 'record'}
for i, d in docs.items():
    for r in refs(d):
        nsid, _, name = r.partition('#')
        nsid = nsid or i
        if nsid.startswith('com.atproto.'): continue
        if nsid not in docs or (name or 'main') not in docs[nsid].get('defs', {}):
            bad.append(f'{i}: ref {r} resolves to nothing here')
    main = d.get('defs', {}).get('main', {})
    if main.get('type') == 'permission-set':
        for perm in main.get('permissions', []):
            for c in perm.get('collection', []):
                if c not in records: bad.append(f'{i}: permission for {c}, which isn\'t a record here')
        missing = records - {c for perm in main.get('permissions', []) for c in perm.get('collection', [])}
        if missing: bad.append(f'{i}: no permission for {sorted(missing)}')
print('\n'.join(bad) or f'{len(docs)} lexicons OK ({len(records)} records)')
sys.exit(1 if bad else 0)
