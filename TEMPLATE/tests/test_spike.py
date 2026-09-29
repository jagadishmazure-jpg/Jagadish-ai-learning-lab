import importlib.util
import pathlib
import sys

_path = pathlib.Path(__file__).resolve().parents[1] / "spike.py"
_spec = importlib.util.spec_from_file_location(f"spike_{_path.parent.name}", _path)
spike = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = spike
_spec.loader.exec_module(spike)


def test_spike_is_deterministic():
    assert spike.evaluate() == spike.evaluate()


def test_candidate_beats_baseline():
    acc = spike.evaluate()["accuracy"]
    assert acc["candidate"] > acc["baseline"]
