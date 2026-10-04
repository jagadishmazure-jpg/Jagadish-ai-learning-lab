import importlib.util
import pathlib
import sys

import pytest

_path = pathlib.Path(__file__).resolve().parents[1] / "spike.py"
_spec = importlib.util.spec_from_file_location("five_arch_spike", _path)
spike = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = spike
_spec.loader.exec_module(spike)

SAMPLE = """# Some lab

## Engineering layers

| Layer | Status | Where |
|---|---|---|
| Business understanding | implemented | a |
| Data understanding | **implemented (emphasis)** | b |
| Loop engineering | not in scope | c |
| Infrastructure engineering | implemented (compile-only) | d |

## Next section

| Business understanding | not in scope | ignored, outside the section |
"""


def test_parse_layers_reads_only_the_section():
    got = spike.parse_layers(SAMPLE)
    assert got == {
        "Business understanding": "implemented",
        "Data understanding": "implemented",
        "Loop engineering": "not in scope",
        "Infrastructure engineering": "compile-only",
    }


def test_parse_layers_accepts_a_subsection_heading():
    nested = "## 3. How it works\n\n### Engineering layers\n\n| Layer | Status | Where |\n|---|---|---|\n"
    nested += "| Agent engineering | implemented | x |\n\n### Next\n\n"
    nested += "| Loop engineering | not in scope | y |\n"
    assert spike.parse_layers(nested) == {"Agent engineering": "implemented"}


def test_missing_section_is_an_error():
    with pytest.raises(ValueError):
        spike.parse_layers("# no table here")


def test_unknown_status_is_an_error():
    with pytest.raises(ValueError):
        spike.normalise("maybe")


def test_snapshot_covers_five_labs_by_twelve_layers():
    m = spike.load_snapshot()
    assert set(m) == set(spike.USE_CASES.values())
    s = spike.summarise(m)
    assert s["cells"] == 60 and s["missing"] == 0
    assert s["layers_covered_by_at_least_one_lab"] == 12
    assert (s["implemented"], s["compile_only"], s["not_in_scope"]) == (49, 5, 6)


def test_only_the_turbine_lab_does_continual_learning():
    m = spike.load_snapshot()
    doing = [lab for lab in m if m[lab]["Continual learning"] == "implemented"]
    assert doing == ["wind-turbine-continual-learning"]


def test_render_has_a_row_per_layer():
    out = spike.render(spike.load_snapshot())
    assert all(layer in out for layer in spike.LAYERS)
