# Best practices for technology spikes

What this lab does to make each spike a fair, repeatable basis for a decision. Each item says
where it is enforced.

## Running a spike

| Practice | Why | Where it is enforced |
|---|---|---|
| Offline and deterministic: fixed seeds, no network | the same numbers on every machine | `tests/test_repo.py::test_no_network_calls_in_spikes`, determinism tests per topic |
| Always compare against a baseline | a number alone does not show a gain | each topic's "How it works" and tests |
| Mock the product, state what is mocked | honesty about what the numbers mean | "Limitations" section in every topic |
| One idea per spike, a few hundred lines | readable in one sitting | review |
| Pin the headline numbers in tests | the page and the code cannot drift | topic tests |
| Paste real output with `scripts/doc_drift.py` | no hand-copied numbers | CI doc-drift step |
| Mask values that vary by run (timings) | deterministic docs | the `sed` masks in topic markers |

## Deciding

| Practice | Why | Where |
|---|---|---|
| Four rings: ADOPT, TRIAL, ASSESS, HOLD | a small, shared vocabulary | `RINGS` in `tests/test_repo.py` |
| The verdict on the topic page is authoritative | one source of truth | radar test |
| Say what would move a topic up or down a ring | decisions get revisited for a reason | "Adopt this" section |
| ADOPT needs a link to code that uses it | adoption is shown, not claimed | topic page test |
| Measure calibration before trusting confidence | routers and gates depend on it | `03-jev-system1-classifier` |

## Writing

| Practice | Why |
|---|---|
| Own words; link sources instead of quoting | originality and attribution |
| Fictional companies and synthetic data | no confidential or personal data |
| Short sections in a fixed order | readers know where to look |
| No dates in prose | pages do not go stale; order is kept by topic number and the changelog |

## Repository hygiene

| Practice | Where |
|---|---|
| Every folder has a README with a file table | `tests/test_repo.py::test_every_folder_has_a_readme` |
| Code owner on every path | `.github/CODEOWNERS` |
| Lint and format | `ruff check . && ruff format --check .` in CI |
| Links checked, external links weekly | `scripts/check_links.py --external`, scheduled CI |
