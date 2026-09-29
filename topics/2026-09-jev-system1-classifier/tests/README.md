# Tests: Jev System 1 classifier spike

Offline tests for [`../spike.py`](../spike.py): the synthetic dataset is deterministic and
balanced, both backends return probabilities that sum to one, the numpy backend's numbers are
pinned, the two-tier router beats tier 1 alone and costs well under half of LLM-only, escalation
grows with the threshold, the ECE maths is right, the mock LLM's error rate matches its setting,
and the Jev adapter is a stub that never opens a socket.

```bash
pytest -q .
```
