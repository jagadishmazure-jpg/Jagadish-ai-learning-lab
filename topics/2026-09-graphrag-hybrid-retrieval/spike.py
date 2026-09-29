"""Spike: hybrid retrieval (vector + graph + SQL + JSON) behind one data access layer.

A tiny supply-chain world is stored four ways:

* text notes, embedded with a hashed bag-of-words vector (numpy) for similarity search,
* a knowledge graph of who owns / supplies / uses / buys what (networkx),
* a relational contracts table (sqlite3, in memory),
* incident records as JSON documents.

Two answerers get the same questions and the same deterministic question parser:

* vector-only: flattens everything into text chunks, retrieves the top-k, reads the answer off
  the retrieved chunks;
* hybrid: uses vector search only to ground the entity name, then walks the graph, runs SQL
  and filters JSON through the DataLayer.

The question parser is a set of regular expressions standing in for an LLM planner, so the
comparison isolates the retrieval strategy. Offline and deterministic.

Run:  python spike.py
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from dataclasses import dataclass

import networkx as nx
import numpy as np

# --------------------------------------------------------------------------- the world

OWNS = [("Apex Holdings", "Apex Metals"), ("Apex Holdings", "Kestrel Optics")]
SUPPLIES = [
    ("Apex Metals", "steel frame"),
    ("Apex Metals", "motor housing"),
    ("Voltcell", "battery pack"),
    ("Kestrel Optics", "camera module"),
]
USED_IN = [
    ("steel frame", "Orion drone"),
    ("battery pack", "Orion drone"),
    ("camera module", "Orion drone"),
    ("steel frame", "Atlas cart"),
    ("battery pack", "Atlas cart"),
    ("camera module", "Lumen scanner"),
    ("motor housing", "Terra pump"),
]
BUYS = [
    ("Northwind", "Orion drone"),
    ("Northwind", "Lumen scanner"),
    ("Contoso Farms", "Atlas cart"),
    ("Contoso Farms", "Terra pump"),
    ("Fabrikam", "Orion drone"),
    ("Tailspin", "Lumen scanner"),
]
CONTRACTS = [  # (customer, product, annual value in USD)
    ("Northwind", "Orion drone", 1_200_000),
    ("Northwind", "Lumen scanner", 300_000),
    ("Contoso Farms", "Atlas cart", 450_000),
    ("Contoso Farms", "Terra pump", 800_000),
    ("Fabrikam", "Orion drone", 950_000),
    ("Tailspin", "Lumen scanner", 220_000),
]
INCIDENTS_JSON = json.dumps(
    [
        {"id": "INC-1", "product": "Orion drone", "severity": "high", "status": "open"},
        {"id": "INC-2", "product": "Atlas cart", "severity": "low", "status": "open"},
        {"id": "INC-3", "product": "Terra pump", "severity": "high", "status": "closed"},
        {"id": "INC-4", "product": "Lumen scanner", "severity": "high", "status": "open"},
    ]
)

TYPES = {
    "holding": {"Apex Holdings"},
    "supplier": {"Apex Metals", "Voltcell", "Kestrel Optics"},
    "component": {"steel frame", "motor housing", "battery pack", "camera module"},
    "product": {"Orion drone", "Atlas cart", "Lumen scanner", "Terra pump"},
    "customer": {"Northwind", "Contoso Farms", "Fabrikam", "Tailspin"},
}


def text_chunks() -> list[str]:
    """The same facts written as short notes, the way they would sit in a wiki or a doc store."""
    chunks = [f"{a} owns {b}." for a, b in OWNS]
    chunks += [f"{a} supplies the {b}." for a, b in SUPPLIES]
    chunks += [f"The {b} uses the {a}." for a, b in USED_IN]
    chunks += [f"{a} buys the {b}." for a, b in BUYS]
    chunks += [f"{c} holds a {p} contract worth ${v:,} a year." for c, p, v in CONTRACTS]
    chunks += [
        f"{r['id']} is a {r['severity']} severity incident on the {r['product']}, status {r['status']}."
        for r in json.loads(INCIDENTS_JSON)
    ]
    chunks.append("Apex Metals ran a supplier outage drill last spring with no customer impact.")
    return chunks


# --------------------------------------------------------------------------- vector search


def embed(text: str, dim: int = 512) -> np.ndarray:
    v = np.zeros(dim)
    toks = re.findall(r"[a-z0-9]+", text.lower())
    for t in toks + [f"{a} {b}" for a, b in zip(toks, toks[1:], strict=False)]:
        v[int(hashlib.md5(t.encode()).hexdigest(), 16) % dim] += 1.0
    n = np.linalg.norm(v)
    return v / n if n else v


class VectorIndex:
    def __init__(self, items: list[str]):
        self.items = items
        self.m = np.stack([embed(x) for x in items])

    def search(self, query: str, k: int) -> list[str]:
        s = self.m @ embed(query)
        order = sorted(range(len(self.items)), key=lambda i: (-s[i], i))
        return [self.items[i] for i in order[:k]]


# --------------------------------------------------------------------------- data access layer


class DataLayer:
    """One interface over the four stores. Callers never touch networkx or sqlite directly."""

    def __init__(self) -> None:
        self.g = nx.DiGraph()
        for kind, edges in (("owns", OWNS), ("supplies", SUPPLIES), ("used_in", USED_IN)):
            self.g.add_edges_from(edges, rel=kind)
        self.g.add_edges_from(((p, c) for c, p in BUYS), rel="sold_to")  # downstream direction
        self.db = sqlite3.connect(":memory:")
        self.db.execute("CREATE TABLE contracts (customer TEXT, product TEXT, annual_value INT)")
        self.db.executemany("INSERT INTO contracts VALUES (?, ?, ?)", CONTRACTS)
        self.incidents = json.loads(INCIDENTS_JSON)
        self.entities = VectorIndex(sorted(set().union(*TYPES.values())))

    def resolve(self, name: str) -> str:
        return self.entities.search(name, 1)[0]

    def downstream(self, entity: str, of_type: str) -> set[str]:
        return {n for n in nx.descendants(self.g, entity) if n in TYPES[of_type]}

    def contract_value(self, products: set[str]) -> int:
        if not products:
            return 0
        q = "SELECT COALESCE(SUM(annual_value), 0) FROM contracts WHERE product IN (%s)"
        return self.db.execute(q % ",".join("?" * len(products)), sorted(products)).fetchone()[0]

    def open_incidents(self, products: set[str], severity: str = "high") -> set[str]:
        return {
            r["id"]
            for r in self.incidents
            if r["product"] in products and r["status"] == "open" and r["severity"] == severity
        }


# --------------------------------------------------------------------------- questions

INTENTS = [
    (r"which components does (.+) supply", "component", "entities"),
    (r"which customers buy the (.+)\?", "customer", "entities"),
    (r"which products depend on (.+)\?", "product", "entities"),
    (r"which customers are affected if (.+) has an outage", "customer", "entities"),
    (r"what annual contract value is at risk if (.+) has an outage", "product", "value"),
    (r"which open high-severity incidents affect products that depend on (.+)\?", "product", "incidents"),
]


def parse(question: str) -> tuple[str, str, str]:
    for pat, target, kind in INTENTS:
        m = re.search(pat, question, re.IGNORECASE)
        if m:
            return m.group(1), target, kind
    raise ValueError(f"no intent for: {question}")


@dataclass(frozen=True)
class Case:
    question: str
    gold: frozenset | int
    hops: int


EVAL = [
    Case("Which components does Apex Metals supply?", frozenset({"steel frame", "motor housing"}), 1),
    Case("Which customers buy the Lumen scanner?", frozenset({"Northwind", "Tailspin"}), 1),
    Case("Which products depend on Voltcell?", frozenset({"Orion drone", "Atlas cart"}), 2),
    Case(
        "Which customers are affected if Apex Metals has an outage?",
        frozenset({"Northwind", "Fabrikam", "Contoso Farms"}),
        3,
    ),
    Case("What annual contract value is at risk if Voltcell has an outage?", 2_600_000, 3),
    Case(
        "Which customers are affected if Apex Holdings has an outage?",
        frozenset({"Northwind", "Fabrikam", "Contoso Farms", "Tailspin"}),
        4,
    ),
    Case(
        "Which open high-severity incidents affect products that depend on Kestrel Optics?",
        frozenset({"INC-1", "INC-4"}),
        3,
    ),
    Case("What annual contract value is at risk if Kestrel Optics has an outage?", 2_670_000, 3),
]


# --------------------------------------------------------------------------- answerers


def answer_vector_only(question: str, index: VectorIndex, k: int = 4):
    _, target, kind = parse(question)
    hits = index.search(question, k)
    text = " ".join(hits)
    if kind == "entities":
        return frozenset(e for e in TYPES[target] if e in text)
    if kind == "value":
        return sum(int(x.replace(",", "")) for h in hits for x in re.findall(r"\$([\d,]+)", h))
    return frozenset(m for h in hits if "high" in h and "open" in h for m in re.findall(r"INC-\d+", h))


def answer_hybrid(question: str, dl: DataLayer):
    phrase, target, kind = parse(question)
    anchor = dl.resolve(phrase)
    if kind == "entities":
        return frozenset(dl.downstream(anchor, target))
    products = dl.downstream(anchor, "product")
    if kind == "value":
        return dl.contract_value(products)
    return frozenset(dl.open_incidents(products))


def score(pred, gold) -> float:
    if isinstance(gold, int):
        return float(pred == gold)
    if not pred:
        return 0.0
    tp = len(pred & gold)
    p, r = tp / len(pred), tp / len(gold)
    return 0.0 if tp == 0 else 2 * p * r / (p + r)


def run_eval(k: int = 4) -> dict:
    index, dl = VectorIndex(text_chunks()), DataLayer()
    rows = []
    for c in EVAL:
        v, h = answer_vector_only(c.question, index, k), answer_hybrid(c.question, dl)
        rows.append(
            {
                "question": c.question,
                "hops": c.hops,
                "vector_only": sorted(v) if isinstance(v, frozenset) else v,
                "hybrid": sorted(h) if isinstance(h, frozenset) else h,
                "vector_score": score(v, c.gold),
                "hybrid_score": score(h, c.gold),
            }
        )

    def mean(key, pred=lambda r: True):
        sel = [r[key] for r in rows if pred(r)]
        return round(sum(sel) / len(sel), 3)

    return {
        "rows": rows,
        "summary": {
            "questions": len(rows),
            "top_k": k,
            "vector_only_mean": mean("vector_score"),
            "hybrid_mean": mean("hybrid_score"),
            "vector_only_single_hop": mean("vector_score", lambda r: r["hops"] == 1),
            "vector_only_multi_hop": mean("vector_score", lambda r: r["hops"] > 1),
            "hybrid_multi_hop": mean("hybrid_score", lambda r: r["hops"] > 1),
            "vector_only_exact": sum(r["vector_score"] == 1.0 for r in rows),
            "hybrid_exact": sum(r["hybrid_score"] == 1.0 for r in rows),
        },
    }


def sweep_k(ks: tuple[int, ...] = (2, 4, 8, 12)) -> dict[int, float]:
    """Does giving vector-only more context close the gap? (Mean score per top-k.)"""
    return {k: run_eval(k)["summary"]["vector_only_mean"] for k in ks}


def main() -> None:
    out = run_eval()
    for r in out["rows"]:
        print(f"[{r['hops']} hop] {r['question']}")
        print(f"    vector-only ({r['vector_score']:.2f}): {r['vector_only']}")
        print(f"    hybrid      ({r['hybrid_score']:.2f}): {r['hybrid']}")
    print(json.dumps(out["summary"], indent=2))
    print("vector-only mean score by top-k:", sweep_k())


if __name__ == "__main__":
    main()
