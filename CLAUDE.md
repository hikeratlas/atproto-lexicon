# Notes for agents

These are the schemas of records in people's own AT Protocol accounts. Once a
record is written, it stays in someone's repository: we can't migrate it.

- Everything is under `com.hikeratlas.temp.*` (beta): breaking changes are
  allowed for now, but say so in hikeratlas/website#130 (edit its draft
  comment and changelog) and in the PR.
- Under the stable names (`com.hikeratlas.*`, without `.temp.`), follow
  AT Protocol's rules: new fields only optional, required fields never
  removed, no type changes. A breaking change needs a new NSID.
- Route keys come from hikeratlas/route-keys (the library); don't describe
  or reimplement its recipe here, link it.
- The website (hikeratlas/website `app/atproto/scope.ts`) must ask for every
  collection here: a new record type means a scope change there.
- Descriptions say what a record and its fields are, factually. Policy
  (licences' meaning, what Hiker Atlas may do, defaults an app picks, how
  writers should behave) belongs in the website's terms, not here.
- Run `python3 scripts/check.py` before pushing.
- Queries (`"type": "query"`, e.g. `com.hikeratlas.temp.getRouteStats`) are
  hikeratlas/atproto-indexer's API, not records: nothing in anyone's
  repository depends on them, so they can be changed or deprecated (say so in
  the PR), they need no scope in the website, and they stay out of
  `authFull.json`. Name them flat, `com.hikeratlas.temp.get<Thing>`, so the
  existing `_lexicon.temp` TXT record covers them. Parameters are scalars or
  arrays of scalars (no refs: they travel in the query string). Deploy the
  indexer's side first: merging publishes the lexicon.
- Merging to main publishes changed lexicons to @hikeratlas.com
  (`scripts/publish.py`): what's on main is what's public. A lexicon in a new
  namespace needs a `_lexicon` DNS TXT record (README); ask the maintainer.
