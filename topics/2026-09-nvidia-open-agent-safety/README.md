# NVIDIA Open Agent Safety Platform

**Ring: ADOPT** · Month: 2026-09 · Spike: [`spike.py`](spike.py) · Tests: [`tests/`](tests/README.md)

## What it is

A reference design from NVIDIA for keeping autonomous agents inside the limits their operator set.
It has two halves:

- **OpenShell** (open source, Apache 2.0) is the secure runtime. Each agent works inside a
  sandbox with kernel-level isolation. A gateway sits on the agent's route to tools and to the
  model, a supervisor orchestrates the sandbox and its policy, and a policy prover checks, before
  the agent starts, that the policy the operator wrote cannot be used to go beyond what the
  operator meant.
- **Sentry** is an optional, independent watchdog that runs on BlueField DPUs, i.e. in separate
  hardware on the node's path to the model. It monitors continuously, keeps a trusted activity
  record that ties agent interactions to policy decisions and tool/data access, and can contain
  or quarantine a drifting agent within milliseconds, even when the host itself is not trusted.

The key design idea: enforcement is **out of band**. The controls are not something the agent can
reach, switch off or talk its way around.

## Why it matters for enterprise

- Agents that run for hours with real credentials will drift (a blocked call, a missing tool, a
  vague instruction). Prompting them to behave is not a control; an independent layer is.
- Default-deny policies with a recorded reason for every decision give security and audit teams
  something they can review, test and sign off.
- A kill switch that lives outside the agent, fed by tamper-evident telemetry, is what makes it
  acceptable to give an agent write access to CRM, ERP or ticketing systems.
- The shared-responsibility split (model lab, enterprise, hardware) maps well onto how cloud
  security is already owned in most companies.

## What I tested

[`spike.py`](spike.py) is a software-only sketch of the two core mechanics, in under 300 lines:

1. **Default-deny policy.** An action (actor, action type, target) runs only if an allow rule
   matches; every decision records the rule or the reason it was refused.
2. **Out-of-band monitor + kill switch.** Every action is written to a hash-chained telemetry log.
   A separate monitor that knows nothing about the policy reads each record and trips a kill
   switch on prompt injection, secret-like data in arguments, an unexpected tool, blocked egress,
   or a runaway loop. The gateway holds the triggering step back and refuses all later actions
   from a quarantined agent.

Ten scenarios: six attacks and four benign traces (including a benign trace that repeats a call
right up to the loop limit, to check for false alarms).

## Results

From `python spike.py` on the lab box (Python 3.13):

| Metric | Result |
|---|---|
| Attacks contained | **6 / 6** (injection x2, exfiltration, unexpected tool, external egress, runaway loop) |
| False quarantines | **0 / 4** benign traces |
| Attack step released before quarantine | 0 (the triggering step is always withheld) |
| Telemetry hash chains valid | 10 / 10; editing one record breaks verification (tested) |
| Containment latency, in process | p50 about 0.003 ms, max about 0.006 ms |

The in-process latency only measures a Python function call from record to kill switch, so it is
not comparable to the platform numbers below, which include the cross-component path.

**What this does not reproduce:** hardware enforcement. BlueField isolation, enforcement at line
speed on the path to the model and attested telemetry cannot be shown in software. In this spike
the enforcement point is a Python check that a compromised process could skip. The policy prover
is also not reproduced; the spike only tests the policy against fixed scenarios.

## Verdict: ADOPT

The pattern (default deny with reasons, out-of-band monitor, kill switch at every gateway) is
cheap to build in software, testable in CI, and clearly improves the story for agents with write
access. The hardware half is a deployment option to evaluate once there is suitable hardware; the
software half is worth having now.

## Adopted into

[Jagadish-azure-ai-integration-platform](https://github.com/jagadishmazure-jpg/Jagadish-azure-ai-integration-platform),
runtime safety layer in [`src/aiip/safety/`](https://github.com/jagadishmazure-jpg/Jagadish-azure-ai-integration-platform/tree/main/src/aiip/safety):
sandboxed tool execution, default-deny policy with recorded reasons, signed audit streams read by
an independent monitor, and a session/actor kill switch enforced in the tool, MCP, A2A and event
gateways. Its safety eval gate: **9 / 9 attack scenarios contained, 0 / 4 false quarantines,
containment p50 about 0.4-0.7 ms** in process (varies by run and machine).

## Sources

- NVIDIA, [NVIDIA Open Agent Safety Platform: A Reference for Continuous In-Silicon Agent Monitoring](https://nvda.ws/4hOkDx7) (NVIDIA Technical Blog, 28 Sep 2026)

## Run it

```bash
python spike.py
pytest -q tests
```
