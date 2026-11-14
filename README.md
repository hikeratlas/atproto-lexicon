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
| `lexicons/com/hikeratlas/temp/defs.json` | shared: route key, point, photo | |
| `lexicons/com/hikeratlas/authFull.json` | the permission set signing in can ask for | |

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

## Publishing (not done yet)

Publishing makes the schemas resolvable by anyone, and lets sign-in ask for
the permission set (`include:com.hikeratlas.authFull`) instead of each
collection. A PDS then shows "Hiker Atlas" and its description when asking,
and adding a collection under `com.hikeratlas.*` (the stable names, too) only
needs the published set updated, not everyone to approve again.

1. An atproto account for Hiker Atlas itself, e.g. `@hikeratlas.com` on
   Bluesky. Its DID (`did:plc:...`) holds the schemas, as
   `com.atproto.lexicon.schema` records keyed by NSID.
2. DNS TXT records pointing each namespace at that DID, one per distinct
   prefix:

       _lexicon.hikeratlas.com             TXT "did=did:plc:..."   (com.hikeratlas.authFull)
       _lexicon.temp.hikeratlas.com        TXT "did=did:plc:..."   (com.hikeratlas.temp.fave, ...)
       _lexicon.actor.temp.hikeratlas.com  TXT "did=did:plc:..."   (com.hikeratlas.temp.actor.profile)

3. Publish with [goat](https://github.com/bluesky-social/goat), logged in as
   that account: `goat lex lint`, then `goat lex publish`, from this
   repository's root.
4. Then the website (hikeratlas/website, `app/atproto/scope.ts`) switches its
   `repo:` scopes to `include:com.hikeratlas.authFull`, keeping `atproto` and
   `blob:*/*`, in the same deploy as its client metadata. People signed in
   already keep their sessions.

## Checks

`python3 scripts/check.py` checks every file parses, its `id` matches its
path, its references resolve, and the permission set names only collections
defined here. CI runs it.
