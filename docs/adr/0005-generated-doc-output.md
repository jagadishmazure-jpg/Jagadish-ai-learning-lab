# 0005: Output and code in the docs are generated and checked in CI

- **Status:** accepted

## Context

Hand-copied results drift from the code: a spike changes and the page still shows the old
numbers.

## Decision

Topic pages mark output with `<!-- output: command -->` and code with `<!-- code: path::name -->`.
`scripts/doc_drift.py` runs the commands and re-reads the code; `--check` fails CI on any
difference. Values that vary by run are masked in the command.

## Consequences

- The numbers on a page are the numbers the code produces.
- Changing a spike means re-running `python scripts/doc_drift.py` before committing.
