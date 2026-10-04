# Five advanced agent architectures and the 12 engineering layers

**Ring: ADOPT** · Month: 2026-09 · Spike: [`spike.py`](spike.py) · Tests: [`tests/`](tests/README.md)

## What it is

A framing for agent projects that go beyond a chat-plus-RAG demo. Five use cases, each stressing a
different capability:

| Use case | The hard part it exercises |
|---|---|
| Multi-signal fusion | combining several noisy, differently timed sensor streams into one risk estimate |
| Multimodal RAG | retrieving and reasoning over images plus text, with calibrated confidence |
| Graph reasoning | planning over a network (roads, assets) where the structure is the knowledge |
| Document intelligence | layout, tables and clauses from messy documents, checked by an auditor agent |
| Continual learning with context gating | learning from evaluated outcomes, but only letting vetted lessons into context |

Alongside it, a checklist of 12 engineering layers every serious agent system has to address:
business understanding, data understanding, knowledge, model, context, semantic, agent, loop,
evaluation, harness, infrastructure engineering, and continual learning.

## Why it matters for enterprise

- The layers make "production ready" concrete. A demo usually covers agent and model engineering
  only; audits, incidents and cost overruns come from the other ten.
- The five use cases map onto real industries (public safety, healthcare research, public works,
  legal/compliance, energy) and each forces a different retrieval and evaluation design.
- Marking each layer implemented / not in scope per project is an honest way to show coverage to
  a reviewer or a customer.

## What I tested

Nothing new was built for this topic; the five architectures were built as full labs, and this
spike checks the coverage claim. [`spike.py`](spike.py) parses the "Engineering layers" table in
each lab README of
[Jagadish-azure-agent-labs](https://github.com/jagadishmazure-jpg/Jagadish-azure-agent-labs)
and prints a 12 x 5 matrix. By default it reads the committed snapshot
[`layers_snapshot.json`](layers_snapshot.json) so it runs offline; `--labs-dir` parses a clone and
`--write-snapshot` refreshes the snapshot.

## Results

From `python spike.py`:

| Metric | Result |
|---|---|
| Labs x layers | 5 x 12 = 60 cells, 0 missing |
| Implemented | 49 |
| Implemented, compile-only (Bicep + Terraform validated, not deployed) | 5 (infrastructure, every lab) |
| Not in scope (declared) | 6 (loop engineering in 2 labs, continual learning in 4) |
| Layers covered by at least one lab | 12 / 12 |

Continual learning is implemented only in the wind-turbine lab, by design; the other labs point to
it rather than faking a feedback loop.

## Verdict: ADOPT

The framing is now how every lab is documented and reviewed. It turned vague "production-grade"
claims into a table a reviewer can check against code.

## Adopted into

[Jagadish-azure-agent-labs](https://github.com/jagadishmazure-jpg/Jagadish-azure-agent-labs):
[disaster-signal-fusion](https://github.com/jagadishmazure-jpg/Jagadish-azure-agent-labs/tree/main/labs/disaster-signal-fusion),
[medical-eye-scan-multimodal](https://github.com/jagadishmazure-jpg/Jagadish-azure-agent-labs/tree/main/labs/medical-eye-scan-multimodal),
[road-network-maintenance-graph](https://github.com/jagadishmazure-jpg/Jagadish-azure-agent-labs/tree/main/labs/road-network-maintenance-graph),
[legal-document-compliance](https://github.com/jagadishmazure-jpg/Jagadish-azure-agent-labs/tree/main/labs/legal-document-compliance),
[wind-turbine-continual-learning](https://github.com/jagadishmazure-jpg/Jagadish-azure-agent-labs/tree/main/labs/wind-turbine-continual-learning).

## Sources

- Idea source: Maryam Miradi, "5 AI Agents Projects to Build in 2026" (YouTube video). The labs,
  the layer definitions as written in them, and this write-up are my own.

## Run it

```bash
python spike.py
python spike.py --labs-dir /path/to/Jagadish-azure-agent-labs/labs
pytest -q tests
```
