# 0002: Four radar rings, with the topic page as the source of truth

- **Status:** accepted

## Context

Without a fixed vocabulary, write-ups end in "promising" or "interesting", which does not tell a
reader whether to build on the technology.

## Decision

Each topic gets one ring: ADOPT (use by default), TRIAL (use where risk is manageable, adoption
planned), ASSESS (understand, do not build on yet) or HOLD (do not start new work, reason
recorded). The ring on the topic page is authoritative; the root README radar is tested against
it. ADOPT requires a link to the code that uses the technology.

## Consequences

- Every topic ends in a decision a reader can act on.
- Moving a ring is a visible change in one commit (page, radar, changelog).
