#!/usr/bin/env python3
"""Checks the lexicons: each file parses, its id matches its path, every ref
resolves to a lexicon here (or com.atproto.*), the permission set names
only collections defined here, and queries (the indexer's API) are well
formed. Queries are not collections: the permission set leaves them out."""
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

# Queries (XRPC, served by hikeratlas/atproto-indexer): parameters may only be
# scalars or arrays of scalars, as they travel in the query string; the
# output is JSON with an object (or ref) schema, or bytes with no schema (an
# image, as com.atproto.sync.getBlob gives a blob: "*/*" or image/*);
# nothing else may be "main".
PARAM_TYPES = {'boolean', 'integer', 'string', 'unknown'}
queries = {i for i, d in docs.items() if d.get('defs', {}).get('main', {}).get('type') == 'query'}
for i in sorted(queries):
    main = docs[i]['defs']['main']
    params = main.get('parameters')
    if params is not None:
        if params.get('type') != 'params': bad.append(f'{i}: parameters must be of type params')
        for name, prop in params.get('properties', {}).items():
            t = prop.get('type')
            if t == 'array': t = prop.get('items', {}).get('type')
            if t not in PARAM_TYPES: bad.append(f'{i}: parameter {name} must be a scalar or an array of scalars')
        for name in params.get('required', []):
            if name not in params.get('properties', {}): bad.append(f'{i}: required parameter {name} isn\'t defined')
    out = main.get('output')
    binary = out is not None and (out.get('encoding') == '*/*' or str(out.get('encoding', '')).startswith('image/'))
    if binary:
        if 'schema' in out: bad.append(f'{i}: a binary output has no schema')
    elif not out or out.get('encoding') != 'application/json':
        bad.append(f'{i}: output must be application/json, or bytes ("*/*" or image/*)')
    elif out.get('schema', {}).get('type') not in ('object', 'ref', 'union'):
        bad.append(f'{i}: output schema must be an object, ref or union')
    for e in main.get('errors', []):
        if not e.get('name'): bad.append(f'{i}: every error needs a name')
    if not i.split('.')[-1].startswith('get'):
        bad.append(f'{i}: query names start with get (getRouteStats)')
    if i in records: bad.append(f'{i}: both a query and a record')

print('\n'.join(bad) or f'{len(docs)} lexicons OK ({len(records)} records, {len(queries)} queries)')
sys.exit(1 if bad else 0)
