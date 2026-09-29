"""Spike template: compare a candidate against a baseline on a seeded synthetic task.

Replace `baseline` and `candidate` with the old way and the new technology (or a mock of it).
Keep it offline: no API keys, no network, fixed seeds.

Run:  python spike.py
"""

from __future__ import annotations

import json
import random


def make_data(n: int = 200, seed: int = 7) -> list[tuple[float, int]]:
    rng = random.Random(seed)
    return [(x, int(x > 0.5)) for x in (rng.random() for _ in range(n))]


def baseline(x: float) -> int:
    return 1  # always predicts the majority-ish class


def candidate(x: float) -> int:
    return int(x > 0.5)


def evaluate(seed: int = 7) -> dict:
    data = make_data(seed=seed)
    acc = {
        name: sum(fn(x) == y for x, y in data) / len(data)
        for name, fn in (("baseline", baseline), ("candidate", candidate))
    }
    return {"n": len(data), "accuracy": acc}


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
