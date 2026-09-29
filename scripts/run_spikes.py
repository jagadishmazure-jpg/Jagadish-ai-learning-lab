"""Run every topic spike (python topics/*/spike.py) from its own folder; exit 1 if any fails."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    failed = []
    for spike in sorted((ROOT / "topics").glob("*/spike.py")):
        print(f"=== {spike.parent.name}", flush=True)
        r = subprocess.run([sys.executable, spike.name], cwd=spike.parent)
        if r.returncode:
            failed.append(spike.parent.name)
    print(f"spikes failed: {failed}" if failed else "all spikes ran")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
