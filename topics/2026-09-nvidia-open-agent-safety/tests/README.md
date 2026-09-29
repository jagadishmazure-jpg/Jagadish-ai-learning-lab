# Tests: NVIDIA Open Agent Safety spike

Offline unit tests for [`../spike.py`](../spike.py): default-deny decisions and their reasons,
all attacks contained with no false quarantines, the triggering step never released, the kill
switch blocking later actions, tamper detection in the telemetry hash chain, and a loose latency
bound (< 50 ms) that holds on shared CI runners.

```bash
pytest -q .
```
