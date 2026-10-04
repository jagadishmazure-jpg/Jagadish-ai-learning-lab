# Scripts

| File | What it does |
|---|---|
| [`new_topic.py`](new_topic.py) | Copies [`TEMPLATE/`](../TEMPLATE/README.md) to `topics/<NN>-<slug>/` with the next number and fills in the title |
| [`check_links.py`](check_links.py) | Checks every Markdown link: local files and anchors always, external URLs with `--external` (404/410 fail, other errors warn) |
| [`run_spikes.py`](run_spikes.py) | Runs every `topics/*/spike.py` and fails if any exits non-zero (used in CI) |
| [`doc_drift.py`](doc_drift.py) | Re-runs the commands and re-reads the code behind every `output:` and `code:` marker in the Markdown; `--check` fails on drift (used in CI) |

```bash
python scripts/new_topic.py my-new-tool "My New Tool"
python scripts/check_links.py --external
python scripts/run_spikes.py
python scripts/doc_drift.py --check
```
