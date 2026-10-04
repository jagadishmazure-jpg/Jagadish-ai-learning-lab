"""Create topics/<NN>-<slug>/ from TEMPLATE/, numbering topics in the order they are studied.

    python scripts/new_topic.py my-new-tool "My New Tool"

Then: write the README, make the spike real, add a TECH RADAR row in the root README and an entry
in CHANGELOG.md (the repo tests fail until both exist).
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOPIC = re.compile(r"(\d{2})-[a-z0-9]+(-[a-z0-9]+)*")


def next_number(root: Path = ROOT) -> str:
    """Two-digit number one higher than the highest existing topic (01 for the first)."""
    names = [p.name for p in (root / "topics").iterdir() if p.is_dir()]
    nums = [int(m.group(1)) for name in names if (m := TOPIC.fullmatch(name))]
    return f"{max(nums, default=0) + 1:02d}"


def create(slug: str, title: str, root: Path = ROOT) -> Path:
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
        raise ValueError("slug must be lowercase words joined by hyphens")
    if any(p.name[3:] == slug for p in (root / "topics").iterdir() if p.is_dir()):
        raise FileExistsError(slug)
    dest = root / "topics" / f"{next_number(root)}-{slug}"
    shutil.copytree(root / "TEMPLATE", dest, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    readme = dest / "README.md"
    text = readme.read_text(encoding="utf-8").replace("{{TITLE}}", title).replace("{{TOPIC}}", dest.name)
    readme.write_text(text, encoding="utf-8")
    return dest


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("title")
    a = ap.parse_args()
    try:
        print(f"created {create(a.slug, a.title).relative_to(ROOT)}")
    except (ValueError, FileExistsError) as e:
        sys.exit(f"error: {e}")
