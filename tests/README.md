# Repository tests

| File | What it does |
|---|---|
| [`test_repo.py`](test_repo.py) | Repository rules for topics, radar, changelog, folder READMEs and scripts |
| [`test_repo_docs.py`](test_repo_docs.py) | Documentation standard: docs set, ADRs, CODEOWNERS, no dates or placeholders, test count; workflow supply-chain guard (pinned actions, permissions, gitleaks, CodeQL, Dependabot) |

`test_repo.py` keeps the lab consistent as topics are added:

- every `topics/<NN>-<slug>/` has a README, a spike, a tests README and at least one test;
- every topic README has the 17 sections in order, a mermaid diagram, generated output and code,
  a ring, a verdict that matches it, sources with links, and an "Adopted into" link when the ring
  is ADOPT;
- the TECH RADAR table in the root README lists every topic with the same ring as its page;
- `CHANGELOG.md` has an entry for every topic;
- every folder has a README (except `.github/`, see the note in the test);
- `scripts/new_topic.py` and the local rules of `scripts/check_links.py` work;
- no spike imports an HTTP client or an LLM SDK.

```bash
pytest -q tests
```
