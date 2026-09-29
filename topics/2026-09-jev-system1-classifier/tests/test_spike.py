import importlib.util
import pathlib
import socket
import sys

import pytest

_path = pathlib.Path(__file__).resolve().parents[1] / "spike.py"
_spec = importlib.util.spec_from_file_location("jev_router_spike", _path)
spike = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = spike
_spec.loader.exec_module(spike)


def test_dataset_is_deterministic_and_balanced():
    a, b = spike.make_dataset(), spike.make_dataset()
    assert a == b and len(a) == 900
    assert {y for _, y in a} == set(spike.LABELS)
    assert sum(y == "billing" for _, y in a) == 300


@pytest.mark.parametrize("backend", ["numpy", "auto"])
def test_choice_probabilities_sum_to_one(backend):
    data = spike.make_dataset()
    model = spike.make_backend(backend).fit([t for t, _ in data], [y for _, y in data])
    c = spike.LocalChoiceClassifier(model).classify("I was charged twice on my invoice")
    assert c.choice == "billing"
    assert abs(sum(c.probabilities.values()) - 1) < 1e-9
    assert c.confidence == max(c.probabilities.values())


def test_numpy_backend_numbers_are_stable():
    r = spike.evaluate("numpy", 0.7)
    assert r["backend"] == "numpy-naive-bayes"
    assert r["tier1_only_accuracy"] == pytest.approx(0.853, abs=1e-3)
    assert r["two_tier"]["escalated"] == pytest.approx(0.040, abs=1e-3)


def test_two_tier_beats_tier1_and_costs_far_less_than_llm_only():
    r = spike.evaluate("auto", 0.7)
    tt, lo = r["two_tier"], r["llm_only"]
    assert tt["accuracy"] > r["tier1_only_accuracy"]
    assert tt["cost_per_1k"] < 0.5 * lo["cost_per_1k"]
    assert 0 < tt["escalated"] < 0.5


def test_higher_threshold_never_escalates_less():
    esc = [s["escalated"] for s in spike.evaluate("auto")["sweep"]]
    assert esc == sorted(esc)


def test_reliability_and_ece():
    import numpy as np

    conf = np.array([0.95, 0.95, 0.55, 0.55])
    correct = np.array([True, True, True, False])
    bins, ece = spike.reliability(conf, correct)
    assert [b["n"] for b in bins] == [2, 2]
    assert ece == pytest.approx(0.5 * 0.05 + 0.5 * 0.05)


def test_mock_llm_error_rate_is_close_to_setting():
    data = spike.make_dataset()
    gold = dict(data)
    llm = spike.MockLLM(gold, error_rate=0.04)
    acc = sum(llm.classify(t).choice == y for t, y in data) / len(data)
    assert 0.93 < acc < 0.99 and llm.calls == len(data)


def test_jev_adapter_is_a_stub_and_never_opens_a_socket(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    adapter = spike.JevChoiceAdapter()
    with pytest.raises(spike.JevNotConfigured):
        adapter.classify("hello", spike.LABELS)
    req = adapter.build_request("refund please", spike.LABELS)
    assert req == {"input": "refund please", "options": list(spike.LABELS)}
    c = adapter.parse_response(
        {"choice": "billing", "confidence": 0.9, "probabilities": {"billing": 0.9, "sales": 0.1}}
    )
    assert c.choice == "billing" and c.probabilities["sales"] == 0.1
