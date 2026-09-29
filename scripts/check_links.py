"""Link check for every tracked Markdown file.

* Relative links must point at a file or folder that exists, and `#anchors` into Markdown files
  must match a heading (GitHub-style slugs).
* With --external, http(s) links are fetched too. 404 and 410 fail the check; other errors
  (timeouts, 403 from bot protection, 429) are reported as warnings, because they say more
  about the remote site's firewall than about the link.

    python scripts/check_links.py [--external]
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
FENCE = re.compile(r"^```.*?^```", re.M | re.S)


def md_files(root: Path = ROOT) -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "*.md"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    return [root / f for f in out if (root / f).is_file()]


def slug(heading: str) -> str:
    h = re.sub(r"[`*_]", "", heading.strip().lower())
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


def anchors(md: Path) -> set[str]:
    text = FENCE.sub("", md.read_text(encoding="utf-8"))
    return {slug(m) for m in re.findall(r"^#{1,6}\s+(.+)$", text, re.M)}


def links(md: Path) -> list[str]:
    return LINK.findall(FENCE.sub("", md.read_text(encoding="utf-8")))


def check_local(md: Path, target: str) -> str | None:
    path, _, frag = target.partition("#")
    dest = (md.parent / path).resolve() if path else md
    if not dest.exists():
        return f"missing target {target}"
    if frag and dest.suffix == ".md" and frag not in anchors(dest):
        return f"missing anchor #{frag} in {dest.relative_to(ROOT)}"
    return None


def check_external(url: str) -> tuple[str, str] | None:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (link-check)"})
    try:
        with urllib.request.urlopen(req, timeout=20):
            return None
    except urllib.error.HTTPError as e:
        return ("error" if e.code in (404, 410) else "warn", f"HTTP {e.code}")
    except Exception as e:  # noqa: BLE001 - network trouble is a warning, not a verdict
        return ("warn", type(e).__name__)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--external", action="store_true")
    a = ap.parse_args()
    errors, warnings, seen, n = [], [], {}, 0
    for md in md_files():
        for target in links(md):
            n += 1
            where = md.relative_to(ROOT)
            if target.startswith(("http://", "https://")):
                if a.external:
                    if target not in seen:
                        seen[target] = check_external(target)
                    r = seen[target]
                    if r:
                        (errors if r[0] == "error" else warnings).append(f"{where}: {target} ({r[1]})")
            elif not target.startswith("mailto:"):
                problem = check_local(md, target)
                if problem:
                    errors.append(f"{where}: {problem}")
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(
        f"checked {n} links ({len(seen)} external URLs fetched): "
        f"{len(errors)} errors, {len(warnings)} warnings"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
