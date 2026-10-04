# Adopt this

How to run a learning lab like this one for your own team.

## The minimum

1. One folder per topic with a write-up, a runnable spike and tests.
2. Offline, seeded spikes compared against a baseline ([ADR 0001](adr/0001-offline-deterministic-spikes.md)).
3. A four-ring radar where every topic ends in a decision ([ADR 0002](adr/0002-tech-radar-rings.md)).
4. ADOPT only with a link to code that uses it.
5. CI that runs every spike and fails when a page drifts from its output ([components/tooling.md](components/tooling.md)).

## Then

- A template that carries the page structure, so new topics start complete.
- A changelog of decisions, so ring changes are explained.
- A weekly external link check, since sources move.

## Per topic

Each topic page ends with its own "Adopt this" steps:

| Topic | Pattern worth taking |
|---|---|
| [01-five-agent-architectures](../topics/01-five-agent-architectures/README.md) | an engineering-layers table per project, parsed in CI |
| [02-graphrag-hybrid-retrieval](../topics/02-graphrag-hybrid-retrieval/README.md) | one data access layer over vector, graph, SQL and JSON |
| [03-jev-system1-classifier](../topics/03-jev-system1-classifier/README.md) | a calibrated classifier in front of the LLM |
| [04-nvidia-open-agent-safety](../topics/04-nvidia-open-agent-safety/README.md) | default deny, out-of-band monitor and a kill switch |

## What not to copy as is

- Mock error rates and simulated prices: replace them with your own measurements.
- The tiny synthetic worlds: they show the shape of a result, not its size.
