# Scripts

| Script | What it does |
|---|---|
| [`new_topic.py`](new_topic.py) | Copies [`TEMPLATE/`](../TEMPLATE/README.md) to `topics/<YYYY-MM>-<slug>/` and fills in the title and month |
| [`check_links.py`](check_links.py) | Checks every Markdown link: local files and anchors always, external URLs with `--external` (404/410 fail, other errors warn) |
| [`run_spikes.py`](run_spikes.py) | Runs every `topics/*/spike.py` and fails if any exits non-zero (used in CI) |

```bash
python scripts/new_topic.py 2026-10 my-new-tool "My New Tool"
python scripts/check_links.py --external
python scripts/run_spikes.py
```
