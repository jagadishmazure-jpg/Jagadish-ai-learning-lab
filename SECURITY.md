# Security

## Scope

This repository holds small offline experiments. It has no services, no deployments and no
credentials: spikes use synthetic data and mocks, and no code calls an external API. The Jev
adapter is a stub with no key and no HTTP client.

## Reporting a problem

If you find something that looks like a secret, personal data, or code that reaches the network,
please open a private report through GitHub's "Report a vulnerability" (Security tab) rather than
a public issue. I aim to reply within a few days.

## Rules the repo follows

- No API keys, tokens or connection strings in code, tests, notebooks or history. A secrets scan
  runs before anything is made public.
- Spikes stay offline; a repository test fails if a spike imports an HTTP client or an LLM SDK.
- Test data is synthetic. No customer, employer or personal data.
- CI runs with read-only repository permissions.
