# Security

## Scope

This repository holds small offline experiments. It has no services, no deployments and no
credentials: spikes use synthetic data and mocks, and no code calls an external API. The Jev
adapter is a stub with no key and no HTTP client.

## Reporting a problem

If you find something that looks like a secret, personal data, or code that reaches the network,
please do not open a public issue with the details.

1. Open a private report through GitHub's "Report a vulnerability" (Security tab).
2. If that button is not shown, open an issue titled `Security contact request` with no technical
   details, and I will reply with a private channel.

I aim to reply within a few days. This is a personal repository maintained by one person, so there
is no formal SLA or bug bounty.

## Rules the repo follows

- No API keys, tokens or connection strings in code, tests, notebooks or history. gitleaks scans
  the full git history in CI, and GitHub secret scanning with push protection is on.
- Spikes stay offline; a repository test fails if a spike imports an HTTP client or an LLM SDK.
- Test data is synthetic. No customer, employer or personal data.
- CI runs with read-only repository permissions.
- **Supply chain:** every third-party GitHub Action is pinned to a full commit SHA with its version in a comment, and every workflow starts from read-only `permissions`. Dependabot proposes weekly, grouped updates ([`.github/dependabot.yml`](.github/dependabot.yml)); CodeQL scans the Python code and the workflow files ([`codeql.yml`](.github/workflows/codeql.yml)); gitleaks scans the full git history in CI. A test (`test_workflows_are_hardened`) fails if an action is left unpinned or a workflow loses its `permissions` block.
- **GitHub settings:** secret scanning with push protection, Dependabot alerts and security updates, private vulnerability reporting, and a ruleset on `main` that blocks force-pushes and branch deletion and requires the CI checks before a pull request can merge. The maintainer (repository admin) can still push directly to `main`, so for direct pushes the checks run after the push rather than before it.
