# Implementation guide

How a topic moves from announcement to decision in this lab, with the files involved at each
step.

## 1. Set up

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest
python scripts/run_spikes.py
```

## 2. Create the topic

```bash
python scripts/new_topic.py my-new-tool "My New Tool"
```

This copies [`TEMPLATE/`](../TEMPLATE/README.md) to the next numbered folder under `topics/`.

## 3. Learn

Read the primary source. Fill in section 1 (Purpose) in your own words: what it is and why an
enterprise would care. Add the source link under "Sources".

## 4. Build the spike

1. Write seeded synthetic data that has both easy and hard cases.
2. Write the baseline: the way the problem is solved today.
3. Write the candidate: the new idea, with any product replaced by a mock or a stub adapter that
   raises if called.
4. Print a table and a JSON summary.
5. Keep it under a few hundred lines.

Worked examples: [`02-graphrag-hybrid-retrieval`](../topics/02-graphrag-hybrid-retrieval/README.md)
(baseline vs candidate on the same parser), [`03-jev-system1-classifier`](../topics/03-jev-system1-classifier/README.md)
(threshold sweep and calibration), [`04-nvidia-open-agent-safety`](../topics/04-nvidia-open-agent-safety/README.md)
(attack and benign scenarios).

## 5. Test

In `tests/test_spike.py`: determinism, the headline numbers (pinned or bounded), and no network
access. For a wrapped API, replace `socket` in the test to prove the stub never connects.

## 6. Document

Fill in sections 2 to 16. Add `output:` and `code:` markers and run:

```bash
python scripts/doc_drift.py topics/<NN>-<slug>/README.md
```

Mask anything that varies by run in the marker's command (see the latency mask in topic 04).

## 7. Decide

Pick the ring and write the verdict in section 17. For ADOPT, link the code that uses it; for
TRIAL, name the planned target. Add the radar row in the root README and an entry in
`CHANGELOG.md`.

## 8. Check

| Check | Command |
|---|---|
| lint and format | `ruff check . && ruff format --check .` |
| tests | `pytest` |
| every spike runs | `python scripts/run_spikes.py` |
| docs match output | `python scripts/doc_drift.py --check` |
| links | `python scripts/check_links.py --external` |

The tooling behind these checks is described in [components/tooling.md](components/tooling.md).
