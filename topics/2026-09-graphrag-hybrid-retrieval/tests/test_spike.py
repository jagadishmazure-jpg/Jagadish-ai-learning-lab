import importlib.util
import pathlib
import sys

import pytest

_path = pathlib.Path(__file__).resolve().parents[1] / "spike.py"
_spec = importlib.util.spec_from_file_location("graphrag_spike", _path)
spike = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = spike
_spec.loader.exec_module(spike)


@pytest.fixture(scope="module")
def dl():
    return spike.DataLayer()


def test_entity_resolution_uses_vector_similarity(dl):
    assert dl.resolve("Apex Metals") == "Apex Metals"
    assert dl.resolve("kestrel optics inc") == "Kestrel Optics"


def test_graph_traversal_multi_hop(dl):
    assert dl.downstream("Voltcell", "product") == {"Orion drone", "Atlas cart"}
    assert dl.downstream("Apex Holdings", "customer") == spike.TYPES["customer"]


def test_sql_and_json_access(dl):
    assert dl.contract_value({"Orion drone"}) == 2_150_000
    assert dl.contract_value(set()) == 0
    assert dl.open_incidents({"Terra pump", "Atlas cart"}) == set()
    assert dl.open_incidents({"Orion drone"}) == {"INC-1"}


def test_hybrid_answers_every_question():
    s = spike.run_eval()["summary"]
    assert s["hybrid_exact"] == s["questions"] == 8
    assert s["hybrid_mean"] == 1.0


def test_vector_only_is_fine_single_hop_but_weak_multi_hop():
    s = spike.run_eval()["summary"]
    assert s["vector_only_single_hop"] == 1.0
    assert s["vector_only_multi_hop"] < 0.5
    assert s["vector_only_mean"] == pytest.approx(0.438, abs=1e-3)


def test_more_context_does_not_close_the_gap():
    assert max(spike.sweep_k().values()) < 0.6


def test_parser_rejects_unknown_questions():
    with pytest.raises(ValueError):
        spike.parse("What is the weather?")


def test_score_f1():
    assert spike.score(frozenset({"a", "b"}), frozenset({"a"})) == pytest.approx(2 / 3)
    assert spike.score(frozenset(), frozenset({"a"})) == 0.0
    assert spike.score(5, 5) == 1.0
