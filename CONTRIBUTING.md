# Contributing

This is a personal learning lab, but the same checks apply to every change, mine included.

## Adding a topic

1. `python scripts/new_topic.py <YYYY-MM> <slug> "<Title>"` (copies [`TEMPLATE/`](TEMPLATE/README.md)).
2. Fill in the write-up in your own words. Link sources; do not paste their text.
3. Keep the spike offline and deterministic (fixed seeds, mocks for any product or model). State
   what is mocked and what the numbers do not show.
4. Pin the headline numbers in tests, so the write-up and the code cannot drift apart.
5. Add the topic to the tech radar in the root README and to [`CHANGELOG.md`](CHANGELOG.md).

## Checks every change must pass

```bash
ruff check . && ruff format --check .
pytest
python scripts/run_spikes.py
python scripts/check_links.py --external
```

CI runs the same commands on every push and pull request.

## Moving a topic between rings

Change the ring on the topic page and in the radar in the same commit, add a CHANGELOG line with
the reason, and, when moving to ADOPT, add the "Adopted into" link to the code that uses it.
