# 0003: Topic folders are numbered, not dated

- **Status:** accepted (replaces the earlier month-prefixed folder names)

## Context

Topic folders were named by the month they were studied. That put dates into paths, links and
docs, and the dates went stale as pages were revised.

## Decision

Topics are named `<NN>-<slug>` and numbered in study order. `scripts/new_topic.py` picks the
next number. The changelog groups changes by batch.

## Consequences

- Order is still visible; no prose or path carries a date.
- Old month-prefixed links break; the only inbound reference (the maturity assessment's evidence
  snapshot) is regenerated.
