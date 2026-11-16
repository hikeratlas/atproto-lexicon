# atproto-lexicon

The AT Protocol schemas ([lexicons](https://atproto.com/specs/lexicon)) of
the records [Hiker Atlas](https://www.hikeratlas.com) writes to people's own
accounts. Faves, tracks and reviews live in your repository on your PDS, not
in a database of ours, so any app can read them and you can take them
anywhere. The proposal is discussed and versioned in hikeratlas/website#130.

All are under `com.hikeratlas.temp.*` while in beta: AT Protocol's
convention for schemas that can still change in breaking ways. Stable
`com.hikeratlas.*` names come when they settle.

| File | Record | Record key |
|---|---|---|
| `lexicons/com/hikeratlas/temp/actor/profile.json` | that an account uses Hiker Atlas, and its settings | `self` |
| `lexicons/com/hikeratlas/temp/fave.json` | a faved route, holding only when | the route's key |
| `lexicons/com/hikeratlas/temp/track.json` | a GPX trace of an outing, a day or a whole multi-day trip | a TID |
| `lexicons/com/hikeratlas/temp/review.json` | a review of a hike | a TID |
| `lexicons/com/hikeratlas/temp/defs.json` | shared: route key, point, photo, and the queries' views | |
| `lexicons/com/hikeratlas/authFull.json` | the permission set signing in can ask for | |

Hiker Atlas's indexer, [atproto-indexer](https://github.com/hikeratlas/atproto-indexer),
gathers everyone's records so hike pages can show them. Its API is defined
here too, as query lexicons (`"type": "query"`), so any app can call it:

| File | Query |
|---|---|
| `lexicons/com/hikeratlas/temp/getRouteStats.json` | faves, reviews and tracks counts for up to 100 route keys |
| `lexicons/com/hikeratlas/temp/getRouteReviews.json` | a route's reviews, newest first |
| `lexicons/com/hikeratlas/temp/getRouteTracks.json` | a route's tracks, newest first |
| `lexicons/com/hikeratlas/temp/getPhoto.json` | a photo of a track or review as an image (a thumbnail, or as uploaded), through a cache |

Queries aren't records: nothing in anyone's account depends on them, so they
may change or be deprecated, they need no permission, and the permission set
leaves them out.

Routes are named by their [route key](https://github.com/hikeratlas/route-keys),
computed from the route's line, so no ids are minted:
`1E57E06gbDEBBBICDGF.tn3dBnAuR_Q`. A fave's record key is the route key
itself.

## Signing in

Hiker Atlas asks for:

    atproto repo:com.hikeratlas.temp.actor.profile repo:com.hikeratlas.temp.fave
      repo:com.hikeratlas.temp.track repo:com.hikeratlas.temp.review blob:*/*

`blob:*/*` (uploading GPX traces and photos) can't be part of a permission
set, so it's always asked for directly.

## Publishing

The lexicons live in Hiker Atlas's own account, [@hikeratlas.com](https://bsky.app/profile/hikeratlas.com)
(`did:plc:7onixtzlmdjijmp7ympxedte`), as `com.atproto.lexicon.schema`
records keyed by NSID, so anyone can resolve them.

- **Publishing is automatic.** Merging a change to `lexicons/` publishes it:
  `.github/workflows/publish.yml` runs `scripts/publish.py`, which writes only
  the schemas that changed. It needs the repository secret `BSKY_APP_PASSWORD`,
  an app password for @hikeratlas.com. Pull requests get a dry run, without it.
- **DNS points each namespace at that account**, one TXT record per distinct
  prefix:

      _lexicon.hikeratlas.com             TXT "did=did:plc:7onixtzlmdjijmp7ympxedte"   (com.hikeratlas.authFull)
      _lexicon.temp.hikeratlas.com        TXT "did=did:plc:7onixtzlmdjijmp7ympxedte"   (com.hikeratlas.temp.fave, ...)
      _lexicon.actor.temp.hikeratlas.com  TXT "did=did:plc:7onixtzlmdjijmp7ympxedte"   (com.hikeratlas.temp.actor.profile)

  A lexicon in a new namespace (say `com.hikeratlas.temp.trip.*`) needs a new
  record.
- **Once these resolve,** the website (hikeratlas/website, `app/atproto/scope.ts`)
  can ask for `include:com.hikeratlas.authFull` instead of each collection,
  keeping `atproto` and `blob:*/*`, in the same deploy as its client metadata.
  People signed in already keep their sessions.

## Checks

`python3 scripts/check.py` checks every file parses, its `id` matches its
path, its references resolve, the permission set names exactly the
collections defined here, and queries are well formed (scalar parameters,
JSON output, a `get` name). CI runs it.
