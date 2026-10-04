# AI Learning Lab

[![ci](https://github.com/jagadishmazure-jpg/Jagadish-ai-learning-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/jagadishmazure-jpg/Jagadish-ai-learning-lab/actions/workflows/ci.yml)

How I keep up with new AI technology and decide what to use. Each new tool, paper or platform
gets a short, runnable spike and a one-page write-up with real numbers and a verdict. The ones
that earn it are adopted into my portfolio repositories, and the page links to where.

## At a glance (for recruiters)

Every topic goes through the same four steps, usually within days of the announcement:

1. **Learn:** read the primary source and write a one-page summary in my own words: what it is,
   why an enterprise would care.
2. **Test:** build a small, offline, deterministic spike that isolates the core idea, compared
   against a baseline, with tests.
3. **Decide:** put it on the tech radar (ADOPT / TRIAL / ASSESS / HOLD) with the numbers behind the
   call and the limits of what the spike shows.
4. **Adopt:** if it earns ADOPT, build it into a real project and link it; TRIAL items name where
   they are planned to go.

Current state: 4 topics, 2 adopted, 2 in trial, 4 spikes and 57 tests running in CI.

```mermaid
flowchart LR
    S[New AI tech<br/>announcement, paper, video] --> L[Learn<br/>one-page write-up]
    L --> T[Test<br/>offline spike + tests]
    T --> D{Decide<br/>radar ring}
    D -->|ADOPT| A[Adopt<br/>built into a portfolio repo]
    D -->|TRIAL| P[Planned adoption<br/>named target repo]
    D -->|ASSESS| W[Watch<br/>revisit later]
    D -->|HOLD| H[Hold<br/>reason recorded]
    A --> C[CHANGELOG + radar updated]
    P --> C
    W --> C
    H --> C
```

## Tech radar

| Ring | Topic | Headline result | Where it went |
|---|---|---|---|
| **ADOPT** | [NVIDIA Open Agent Safety Platform](topics/04-nvidia-open-agent-safety/) | default-deny + out-of-band kill switch: 6/6 attacks contained, 0/4 false quarantines | [integration platform `src/aiip/safety/`](https://github.com/jagadishmazure-jpg/Jagadish-azure-ai-integration-platform/tree/main/src/aiip/safety) (9/9 contained, 0/4 false, p50 about 0.4-0.7 ms) |
| **ADOPT** | [Five agent architectures + 12 engineering layers](topics/01-five-agent-architectures/) | 5 labs x 12 layers: 49 implemented, 5 compile-only, 6 declared out of scope, 0 missing | [Jagadish-azure-agent-labs](https://github.com/jagadishmazure-jpg/Jagadish-azure-agent-labs) |
| **TRIAL** | [Jev as a "System 1" classifier](topics/03-jev-system1-classifier/) | two-tier router: 0.970 accuracy, 16.7% escalated, $0.27 vs $1.50 per 1k (LLM only) | rules-based System 1 router in [Jagadish-azure-finops](https://github.com/jagadishmazure-jpg/Jagadish-azure-finops/blob/main/src/finops/ai/routing.py); planned: calibrated tier 1 there and in the integration platform router |
| **TRIAL** | [GraphRAG hybrid retrieval](topics/02-graphrag-hybrid-retrieval/) | hybrid 8/8 vs vector-only 3/8; multi-hop score 1.00 vs 0.25 | partly in [agentic-ai project 15](https://github.com/jagadishmazure-jpg/Jagadish-agentic-ai/tree/main/projects/15-banking-credit-memo) and the [agent platform knowledge layer](https://github.com/jagadishmazure-jpg/Jagadish-azure-agent-platform/tree/main/src/agentplatform/knowledge); planned: unified data layer |

Rings: **ADOPT** use it by default; **TRIAL** worth using where the risk is manageable, adoption
planned; **ASSESS** worth understanding, not yet worth building on; **HOLD** do not start new work
with it (the page says why). No topic is in ASSESS or HOLD yet.

## Honest note: what the spikes are and are not

- Every spike runs **offline** with deterministic mocks, synthetic data and fixed seeds. No API
  keys, no network calls, no cloud account. Clone it and you get the same numbers.
- Mocks stand in for the real products (for example the "LLM" in the Jev spike is a mock with a
  set error rate, and the Jev adapter is a stub that never calls the API). The write-ups say
  exactly what is mocked and what the numbers do not show.
- Hardware features (such as BlueField enforcement in the NVIDIA topic) cannot be reproduced in
  software and are not claimed.
- Spikes are small on purpose: they test one idea well enough to make a decision, not to be a
  product. The adoption repos are where the production-style work lives.

## Add a new topic

```bash
python scripts/new_topic.py my-new-tool "My New Tool"   # copies TEMPLATE/ to topics/05-my-new-tool/
```

Then, in the new `topics/05-my-new-tool/` folder:

1. Write `README.md` in the template's 17 sections (purpose, architecture, how it works, ...,
   adopt this with the verdict), with real output pasted by `python scripts/doc_drift.py`, and
   the sources linked.
2. Make `spike.py` real: offline, seeded, compared against a baseline, under a few hundred lines.
3. Add tests in `tests/` that pin the headline numbers and prove no network access happens.
4. Add a row to the **Tech radar** table above and an entry in
   [`CHANGELOG.md`](CHANGELOG.md). The repo tests fail until both exist.
5. Run `ruff check . && ruff format --check . && pytest && python scripts/doc_drift.py --check && python scripts/check_links.py`.

The template is in [`TEMPLATE/`](TEMPLATE/README.md); the rules are in
[`CONTRIBUTING.md`](CONTRIBUTING.md).

## Repository layout

| Path | What is there |
|---|---|
| [`topics/`](topics/README.md) | One folder per topic: `README.md` write-up, `spike.py`, `tests/` |
| [`TEMPLATE/`](TEMPLATE/README.md) | Starting point for a new topic |
| [`scripts/`](scripts/README.md) | New-topic generator, link checker, spike runner |
| [`tests/`](tests/README.md) | Repository rules (radar, changelog, READMEs, layout) |
| [`docs/`](docs/README.md) | Best practices, ADRs, why there is no infrastructure, implementation guide, adopt-this checklist, tooling doc |
| [`CHANGELOG.md`](CHANGELOG.md) | What was learned and decided, by batch of topics |
| [`SECURITY.md`](SECURITY.md) · [`CONTRIBUTING.md`](CONTRIBUTING.md) | Reporting problems, checks every change must pass |

CI (GitHub Actions, [`.github/workflows/ci.yml`](.github/workflows/ci.yml)) runs ruff, pytest,
every spike, the doc-drift check and the link check on each push. There is no cloud
infrastructure on purpose: see [docs/no-infrastructure.md](docs/no-infrastructure.md).

## Run it

```bash
git clone https://github.com/jagadishmazure-jpg/Jagadish-ai-learning-lab.git
cd Jagadish-ai-learning-lab
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest                         # all tests, offline
python scripts/run_spikes.py   # every spike, prints its results
```

## Related repositories

[Jagadish-agentic-ai](https://github.com/jagadishmazure-jpg/Jagadish-agentic-ai) ·
[Jagadish-azure-agent-platform](https://github.com/jagadishmazure-jpg/Jagadish-azure-agent-platform) ·
[Jagadish-azure-agent-labs](https://github.com/jagadishmazure-jpg/Jagadish-azure-agent-labs) ·
[Jagadish-azure-ai-integration-platform](https://github.com/jagadishmazure-jpg/Jagadish-azure-ai-integration-platform)

MIT licensed. Written by Jagadish Meduri; source material is linked, not copied.
