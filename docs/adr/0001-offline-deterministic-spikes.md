# 0001: Spikes run offline with seeded data and mocks

- **Status:** accepted

## Context

New AI products are announced faster than they can be trialled on real systems. A decision needs
evidence, but live API calls need keys, cost money and give different numbers each run.

## Decision

Every spike runs offline: synthetic data from a fixed seed, mocks or stub adapters for any
product or model, no HTTP client or LLM SDK imports. Each spike compares the candidate with a
baseline.

## Consequences

- Anyone can reproduce the numbers; CI runs every spike.
- The numbers show the mechanism, not the product's real quality. Every page says what is mocked.
- Questions that need a live service are measured later, in the repository the topic is adopted
  into (see [0004](0004-no-infrastructure.md)).
