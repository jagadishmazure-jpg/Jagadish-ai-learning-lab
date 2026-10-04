# 0004: No cloud infrastructure in this repository

- **Status:** accepted

## Context

The other portfolio repositories carry Bicep, Terraform and gated deploy pipelines. A learning
lab could copy them.

## Decision

This repository has no infrastructure as code and deploys nothing. Spikes run on CI runners.
Topics that reach ADOPT are built, with infrastructure, in their target repository. The full
reasoning and the minimal footprint that would be acceptable are in
[../no-infrastructure.md](../no-infrastructure.md).

## Consequences

- No keys, identities or cloud cost to manage here.
- Live measurements happen in the target repository's dev environment.
