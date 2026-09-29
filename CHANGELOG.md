# Changelog

What I learned and decided, grouped by month. Newest month first.

## 2026-09

- **Added** `2026-09-nvidia-open-agent-safety`: NVIDIA Open Agent Safety Platform (OpenShell
  runtime + Sentry on BlueField). Spike: default-deny policy with reasons and an out-of-band
  monitor with a kill switch; 6/6 attacks contained, 0/4 false quarantines. **ADOPT**, already
  built into the integration platform's runtime safety layer.
- **Added** `2026-09-jev-system1-classifier`: Jev choice API as a fast classifier in front of an
  LLM. Spike: two-tier router with a calibration check; at threshold 0.7, accuracy 0.970 with
  16.7% escalated and $0.27 vs $1.50 per 1k requests. **TRIAL**; Jev adapter is a stub.
- **Added** `2026-09-graphrag-hybrid-retrieval`: vector + graph + SQL + JSON behind one data
  layer. Spike: hybrid 8/8 vs vector-only 3/8 on an 8-question eval. **TRIAL**, partly adopted.
- **Added** `2026-09-five-agent-architectures`: five advanced agent use cases and the 12
  engineering layers. Spike: coverage matrix parsed from the agent-labs READMEs (49 implemented,
  5 compile-only, 6 out of scope, 0 missing). **ADOPT** in Jagadish-azure-agent-labs.
- **Added** the lab itself: tech radar, topic template and generator, repository rules tests,
  link checker, CI (ruff, pytest, spikes, link check).
