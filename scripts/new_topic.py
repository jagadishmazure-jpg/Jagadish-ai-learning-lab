"""Create topics/<YYYY-MM>-<slug>/ from TEMPLATE/.

    python scripts/new_topic.py 2026-10 my-new-tool "My New Tool"

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


def create(month: str, slug: str, title: str, root: Path = ROOT) -> Path:
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month):
        raise ValueError("month must be YYYY-MM")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
        raise ValueError("slug must be lowercase words joined by hyphens")
    dest = root / "topics" / f"{month}-{slug}"
    if dest.exists():
        raise FileExistsError(dest)
    shutil.copytree(root / "TEMPLATE", dest, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    readme = dest / "README.md"
    text = readme.read_text(encoding="utf-8").replace("{{TITLE}}", title).replace("{{MONTH}}", month)
    readme.write_text(text, encoding="utf-8")
    return dest


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("month")
    ap.add_argument("slug")
    ap.add_argument("title")
    a = ap.parse_args()
    try:
        print(f"created {create(a.month, a.slug, a.title).relative_to(ROOT)}")
    except (ValueError, FileExistsError) as e:
        sys.exit(f"error: {e}")
