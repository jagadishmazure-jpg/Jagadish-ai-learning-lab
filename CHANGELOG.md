# Changelog

What I learned and decided, grouped by batch of topics. Newest batch first.

## Repository security

- **Added** supply-chain controls: every GitHub Action pinned to a commit SHA with a version
  comment, a gitleaks job over the full git history, a CodeQL workflow, `.github/dependabot.yml`
  and a guard test (`test_workflows_are_hardened`). `SECURITY.md` gains a fallback contact.
- **Changed** repository settings: Dependabot alerts and security updates, private vulnerability
  reporting and a `main` ruleset (no force-push or deletion; CI required on pull requests).

## Batch 2: documentation and repository standards

- **Changed** topic folders are numbered in study order (`01-` to `04-`) instead of carrying a
  month; `scripts/new_topic.py` picks the next number.
- **Changed** topic pages and the template use the 17-section format; real output and code
  excerpts are pasted and checked by `scripts/doc_drift.py` (new CI step).
- **Changed** `01-five-agent-architectures` parser accepts the Engineering layers table as a
  subsection, matching the agent-labs README format.
- **Fixed** `03-jev-system1-classifier`: the FinOps repo is published and already has a
  rules-based System 1 router; the page and radar say so.
- **Added** `docs/`: best practices, ADRs, why there is no infrastructure, implementation guide,
  adopt-this checklist and a tooling doc; `.github/CODEOWNERS`.

## Batch 1

- **Added** `04-nvidia-open-agent-safety`: NVIDIA Open Agent Safety Platform (OpenShell
  runtime + Sentry on BlueField). Spike: default-deny policy with reasons and an out-of-band
  monitor with a kill switch; 6/6 attacks contained, 0/4 false quarantines. **ADOPT**, already
  built into the integration platform's runtime safety layer.
- **Added** `03-jev-system1-classifier`: Jev choice API as a fast classifier in front of an
  LLM. Spike: two-tier router with a calibration check; at threshold 0.7, accuracy 0.970 with
  16.7% escalated and $0.27 vs $1.50 per 1k requests. **TRIAL**; Jev adapter is a stub.
- **Added** `02-graphrag-hybrid-retrieval`: vector + graph + SQL + JSON behind one data
  layer. Spike: hybrid 8/8 vs vector-only 3/8 on an 8-question eval. **TRIAL**, partly adopted.
- **Added** `01-five-agent-architectures`: five advanced agent use cases and the 12
  engineering layers. Spike: coverage matrix parsed from the agent-labs READMEs (49 implemented,
  5 compile-only, 6 out of scope, 0 missing). **ADOPT** in Jagadish-azure-agent-labs.
- **Added** the lab itself: tech radar, topic template and generator, repository rules tests,
  link checker, CI (ruff, pytest, spikes, link check).
