# Tests: five agent architectures spike

Offline tests for [`../spike.py`](../spike.py): the parser reads only the "Engineering layers"
section, normalises statuses (including bold and "compile-only" variants), rejects unknown
statuses and missing sections, and the committed snapshot covers 5 labs x 12 layers with the
expected counts.

```bash
pytest -q .
```
