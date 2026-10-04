# GraphRAG: hybrid retrieval behind one data access layer

**Ring: TRIAL** · Month: 2026-09 · Spike: [`spike.py`](spike.py) · Tests: [`tests/`](tests/README.md)

## What it is

GraphRAG, in the broad sense used here, means grounding an agent in more than a vector index. The
retriever combines four kinds of access:

- **vector similarity** over text, to find things by meaning and to ground fuzzy names,
- **knowledge-graph traversal**, to follow relationships (owns, supplies, used in, sold to) as far
  as the question needs,
- **relational facts** (SQL), for exact numbers and aggregates,
- **JSON records**, for semi-structured operational data such as incidents or tickets.

All four sit behind one data access layer, so the planner asks for "customers downstream of X" or
"contract value for these products" and never talks to a graph library or a database directly.

## Why it matters for enterprise

- The questions people actually ask are multi-hop: "if this supplier fails, which customers and
  how much revenue?" Vector search returns passages that *look* similar; it does not follow a
  chain, and it cannot add up numbers it did not retrieve.
- Enterprise data already lives in all four shapes. A single access layer lets each store keep
  its own security model and lets the agent's tools stay small and auditable.
- Answers become explainable: the traversal path and the SQL are the citation.

## What I tested

[`spike.py`](spike.py) stores a small supply-chain world (a holding company, 3 suppliers, 4
components, 4 products, 4 customers, 6 contracts, 4 incidents) four ways: text notes embedded with
a hashed bag-of-words vector in numpy, a directed graph in networkx, a contracts table in in-memory
sqlite3, and incident records as JSON.

Two answerers get the same 8 questions and the same regex question parser (a stand-in for an LLM
planner, so only the retrieval strategy differs):

- **vector-only:** every fact flattened into 30 text chunks; retrieve top-k and read the answer off
  the retrieved text (entities of the asked type, or the sum of the dollar amounts it sees);
- **hybrid:** vector search to resolve the entity name, then graph traversal, then SQL or JSON
  through the `DataLayer`.

Scoring: F1 for set answers, exact match for numbers. Questions range from 1 hop ("which
components does Apex Metals supply?") to 4 hops ("which customers are affected if Apex Holdings
has an outage?", i.e. holding -> suppliers -> components -> products -> customers).

## Results

From `python spike.py` (top-k = 4 for vector-only):

| Metric | Vector-only | Hybrid |
|---|---|---|
| Mean score, all 8 questions | 0.438 | **1.000** |
| Single-hop questions (2) | 1.000 | 1.000 |
| Multi-hop questions (6) | 0.250 | **1.000** |
| Fully correct answers | 3 / 8 | **8 / 8** |
| Contract value at risk, Voltcell outage (gold $2,600,000) | $1,250,000 | $2,600,000 |
| Contract value at risk, Kestrel Optics outage (gold $2,670,000) | $1,250,000 | $2,670,000 |

More context does not close the gap: vector-only mean score is 0.375 / 0.438 / 0.521 / 0.529 at
top-k 2 / 4 / 8 / 12. Larger k brings in more of the right chunks but also more wrong entities.

One honest caveat: vector-only got the incidents question right, but by coincidence. It retrieved
incident notes by similarity and filtered for "open" and "high"; in this dataset every open,
high-severity incident happens to be on a product that depends on the asked supplier.

The world is tiny and the parser is hand-written, so the absolute numbers mean little. The shape of
the result (equal on one hop, a large gap from two hops on) is the finding.

## Verdict: TRIAL

Clear win on multi-hop and aggregate questions, no loss on simple lookups. It stays in TRIAL
because the hard parts are not in this spike: keeping the graph in sync with source systems,
entity resolution at scale, per-store access control, and letting an LLM planner choose the
access path reliably.

## Adoption status

Partially adopted already:

- [Jagadish-agentic-ai project 15](https://github.com/jagadishmazure-jpg/Jagadish-agentic-ai/tree/main/projects/15-banking-credit-memo)
  (banking credit memo): graph RAG over beneficial ownership over time.
- [Jagadish-azure-agent-platform knowledge layer](https://github.com/jagadishmazure-jpg/Jagadish-azure-agent-platform/tree/main/src/agentplatform/knowledge):
  entity graph alongside search for the mortgage workflow.

Planned: a unified data access layer in the agent platform, shaped like `DataLayer` here (vector,
graph, SQL, JSON behind one interface), replacing store-specific calls in the agents.

## Sources

- Microsoft Research, [GraphRAG project](https://microsoft.github.io/graphrag/) (background on graph-based retrieval)
- NetworkX, [documentation](https://networkx.org/documentation/stable/)
- Python, [sqlite3 module](https://docs.python.org/3/library/sqlite3.html)

## Run it

```bash
python spike.py
pytest -q tests
```
