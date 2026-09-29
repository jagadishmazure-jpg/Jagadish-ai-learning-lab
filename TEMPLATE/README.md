# {{TITLE}}

**Ring: ASSESS** · Month: {{MONTH}} · Spike: [`spike.py`](spike.py) · Tests: [`tests/`](tests/README.md)

> Template for a new topic. Create a copy with
> `python scripts/new_topic.py <YYYY-MM> <slug> "<Title>"`, then replace every placeholder.
> Keep it to one page. Write in your own words; link sources instead of quoting them.

## What it is

Two or three sentences a non-specialist can follow. Name the vendor or project and the version.

## Why it matters for enterprise

Bullets: the cost, risk, speed or compliance problem it addresses, and for whom.

## What I tested

What the spike does, what is mocked, the dataset (synthetic, seeded), and the baseline it is
compared against. The spike must run offline and give the same numbers every run.

## Results

A table of real numbers copied from `python spike.py`. Say what the numbers do not show.

## Verdict: ASSESS

One of ADOPT / TRIAL / ASSESS / HOLD, with the reason, and what would move it up or down a ring.

## Adopted into

Link to the repo and folder that uses it (ADOPT), or the planned target (TRIAL), or "not adopted".

## Sources

- Author or vendor, linked title of the announcement, paper or article

## Run it

```bash
python spike.py
pytest -q tests
```
