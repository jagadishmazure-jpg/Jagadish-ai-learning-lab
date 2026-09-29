"""Spike: print the 12-layer coverage matrix for the five agent architectures.

The five architectures were built as labs in Jagadish-azure-agent-labs. Each lab README has an
"Engineering layers" table (Layer | Status | Where). This script parses those tables and prints
one matrix, so the coverage claim can be checked rather than taken on trust.

    python spike.py                                   # read the committed snapshot (offline)
    python spike.py --labs-dir ../Jagadish-azure-agent-labs/labs            # parse a clone
    python spike.py --labs-dir <clone>/labs --write-snapshot                # refresh snapshot
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SNAPSHOT = HERE / "layers_snapshot.json"

# use case (from the idea source) -> lab folder that implements it
USE_CASES = {
    "multi-signal fusion": "disaster-signal-fusion",
    "multimodal RAG": "medical-eye-scan-multimodal",
    "graph reasoning": "road-network-maintenance-graph",
    "document intelligence": "legal-document-compliance",
    "continual learning with context gating": "wind-turbine-continual-learning",
}

LAYERS = [
    "Business understanding",
    "Data understanding",
    "Knowledge engineering",
    "Model engineering",
    "Context engineering",
    "Semantic engineering",
    "Agent engineering",
    "Loop engineering",
    "Evaluation engineering",
    "Harness engineering",
    "Infrastructure engineering",
    "Continual learning",
]

SYMBOL = {"implemented": "Y", "compile-only": "C", "not in scope": "-"}


def normalise(status: str) -> str:
    s = status.replace("*", "").strip().lower()
    if s.startswith("not in scope"):
        return "not in scope"
    if "compile-only" in s:
        return "compile-only"
    if s.startswith("implemented"):
        return "implemented"
    raise ValueError(f"unknown status: {status!r}")


def parse_layers(markdown: str) -> dict[str, str]:
    """Return {layer: status} from the '## Engineering layers' table of a lab README."""
    m = re.search(r"^## Engineering layers\s*$(.*?)(?=^## |\Z)", markdown, re.M | re.S)
    if not m:
        raise ValueError("no '## Engineering layers' section")
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0] in LAYERS:
            out[cells[0]] = normalise(cells[1])
    return out


def from_labs_dir(labs_dir: Path) -> dict[str, dict[str, str]]:
    return {
        lab: parse_layers((labs_dir / lab / "README.md").read_text(encoding="utf-8"))
        for lab in USE_CASES.values()
    }


def load_snapshot() -> dict[str, dict[str, str]]:
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))["labs"]


def summarise(matrix: dict[str, dict[str, str]]) -> dict:
    cells = [matrix[lab].get(layer, "missing") for lab in matrix for layer in LAYERS]
    return {
        "labs": len(matrix),
        "layers": len(LAYERS),
        "cells": len(cells),
        "implemented": cells.count("implemented"),
        "compile_only": cells.count("compile-only"),
        "not_in_scope": cells.count("not in scope"),
        "missing": cells.count("missing"),
        "layers_covered_by_at_least_one_lab": sum(
            any(matrix[lab].get(layer) in ("implemented", "compile-only") for lab in matrix)
            for layer in LAYERS
        ),
    }


def render(matrix: dict[str, dict[str, str]]) -> str:
    labs = list(USE_CASES.values())
    short = [lab.split("-")[0][:8] for lab in labs]
    lines = [f"{'layer':28}" + "".join(f"{s:>10}" for s in short)]
    for layer in LAYERS:
        row = "".join(f"{SYMBOL.get(matrix[lab].get(layer, ''), '?'):>10}" for lab in labs)
        lines.append(f"{layer:28}{row}")
    lines.append("Y implemented · C implemented, compile-only (IaC validated, not deployed) · - not in scope")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--labs-dir", type=Path)
    ap.add_argument("--write-snapshot", action="store_true")
    a = ap.parse_args()
    matrix = from_labs_dir(a.labs_dir) if a.labs_dir else load_snapshot()
    if a.write_snapshot:
        payload = {
            "source": "https://github.com/jagadishmazure-jpg/Jagadish-azure-agent-labs",
            "labs": matrix,
        }
        SNAPSHOT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    for use_case, lab in USE_CASES.items():
        print(f"{use_case:40} -> labs/{lab}")
    print(render(matrix))
    print(json.dumps(summarise(matrix), indent=2))


if __name__ == "__main__":
    main()
