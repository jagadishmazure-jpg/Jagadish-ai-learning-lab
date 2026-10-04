# 0006: Topic pages use the same 17 sections as the other portfolio repos

- **Status:** accepted

## Context

Topic pages had six sections. The other portfolio repositories document every component and lab
in a 17-section format, which makes them easy to compare and review.

## Decision

Topic pages and the template use the 17 sections (purpose through adopt this). The verdict and
the adoption link live in "Adopt this"; sources follow as an unnumbered section.
`tests/test_repo.py` checks the order.

## Consequences

- Pages are longer, but every reader finds guardrails, failure modes and Azure mapping in the
  same place.
- The template carries the structure, so new topics start complete.
