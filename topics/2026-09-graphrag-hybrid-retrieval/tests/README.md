# Tests: GraphRAG hybrid retrieval spike

Offline tests for [`../spike.py`](../spike.py): entity names resolve through vector similarity,
graph traversal follows multiple hops, the SQL and JSON accessors return the right values, the
hybrid answerer gets all 8 questions right, vector-only is fine on single-hop and weak on
multi-hop questions (score pinned), a larger top-k does not close the gap, and the question
parser rejects questions it does not know.

```bash
pytest -q .
```
