# Repository tests

[`test_repo.py`](test_repo.py) keeps the lab consistent as topics are added:

- every `topics/<YYYY-MM>-<slug>/` has a README, a spike, a tests README and at least one test;
- every topic README has the required sections, a ring, a verdict that matches it, sources with
  links, and an "Adopted into" link when the ring is ADOPT;
- the TECH RADAR table in the root README lists every topic with the same ring as its page;
- `CHANGELOG.md` has a month section and an entry for every topic;
- every folder has a README (except `.github/`, see the note in the test);
- `scripts/new_topic.py` and the local rules of `scripts/check_links.py` work;
- no spike imports an HTTP client or an LLM SDK.

```bash
pytest -q tests
```
