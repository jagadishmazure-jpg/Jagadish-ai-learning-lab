# Tests (template)

Starter tests for [`../spike.py`](../spike.py). Every topic needs at least: the spike is
deterministic, the headline numbers in the write-up are pinned or bounded, and no network access
happens (patch `socket` if the topic wraps an external API).

```bash
pytest -q .
```
