# Why this repo has no infrastructure

The other portfolio repositories carry Bicep, Terraform and gated deploy pipelines. This one does
not, on purpose.

## The reasons

1. **A spike answers one question.** "Does default-deny plus an out-of-band monitor contain these
   attacks?" or "does a calibrated tier 1 cut cost at equal quality?" can be answered on a laptop
   with seeded data. Provisioning cloud resources would add cost and setup time without changing
   the answer.
2. **Reproducibility beats realism at this stage.** Anyone can clone the repo and get the same
   numbers. A spike that calls a live service gives different numbers every run and needs keys.
3. **Adoption is where infrastructure belongs.** When a topic reaches ADOPT it is built into a
   portfolio repository that already has infrastructure as code, identity, eval gates and a gated
   deploy. Duplicating that here would create a second, weaker copy to maintain.
4. **No secrets to manage.** With no cloud resources there are no keys, no service principals and
   no OIDC trust to secure. `tests/test_repo.py` checks that no spike imports an HTTP client or an
   LLM SDK.

## What runs instead

| Need | How it is met |
|---|---|
| compute | GitHub Actions runners (`.github/workflows/ci.yml`) |
| repeatable data | seeded synthetic data inside each `spike.py` |
| model or vendor API | a mock or a stub adapter that raises if called |
| evidence | numbers pinned in tests and output pasted by `scripts/doc_drift.py` |

## When a topic needs a real service

Some questions cannot be answered offline (vendor latency, real calibration on production
traffic, hardware isolation). The process for those is:

1. Keep the offline spike as the baseline and the contract (the same interface the real adapter
   will implement).
2. Run the live measurement in the target repository's dev environment, which already has
   managed identity, budgets and teardown, not here.
3. Record the live numbers on the topic page next to the offline ones and say which is which.

## Minimal infrastructure, if it is ever added

If a future topic needs its own resources, the smallest acceptable footprint is: one resource
group per topic, a budget alert, a user-assigned managed identity, OIDC login from GitHub
Actions, and a teardown workflow that runs after the measurement. It would follow the same
patterns as the deploy workflows in the agent platform and agent labs repositories. None of this
exists today, and the radar does not depend on it.
