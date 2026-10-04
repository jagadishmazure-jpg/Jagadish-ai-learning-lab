import importlib.util
import pathlib
import sys

_path = pathlib.Path(__file__).resolve().parents[1] / "spike.py"
_spec = importlib.util.spec_from_file_location("agent_safety_spike", _path)
spike = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = spike
_spec.loader.exec_module(spike)


def test_default_deny_refuses_unknown_action():
    d = spike.Policy().check("support-agent", "tool", "payments.transfer")
    assert not d.allowed and d.reason.startswith("default deny")


def test_allow_decision_names_the_rule():
    d = spike.Policy().check("support-agent", "tool", "crm.get_account")
    assert d.allowed and d.reason == "allowed by r1-crm-read"


def test_other_actor_gets_nothing():
    assert not spike.Policy().check("billing-agent", "tool", "crm.get_account").allowed


def test_every_attack_contained_and_no_false_quarantines():
    s = spike.run_all()["summary"]
    assert s["contained"] == s["attacks"] == 6
    assert s["false_quarantines"] == 0 and s["benign"] == 4


def test_attack_step_is_never_released():
    for r in spike.run_all()["scenarios"]:
        if r["kind"] == "attack":
            # the step that triggered quarantine, and every later step, is withheld
            first_q = r["results"].index("quarantined")
            assert all(x == "quarantined" for x in r["results"][first_q:])


def test_expected_detectors():
    got = {r["id"]: r["detector"] for r in spike.run_all()["scenarios"]}
    assert got["attack.runaway-loop"] == "runaway_loop"
    assert got["attack.exfil-in-args"] == "data_exfiltration"
    assert got["attack.unexpected-tool"] == "unexpected_tool"
    assert got["attack.external-egress"] == "blocked_egress"


def test_kill_switch_blocks_all_later_actions():
    tel, ks = spike.Telemetry(), spike.KillSwitch()
    gw = spike.Gateway(spike.Policy(), tel, spike.Monitor(ks, spike.EXPECTED_TOOLS), ks)
    assert gw.act("support-agent", "tool", "crm.get_account", "ACC-1") == "ok"
    ks.trip("support-agent", "manual", tel.records[-1]["t"])
    assert gw.act("support-agent", "tool", "crm.get_account", "ACC-1") == "quarantined"


def test_telemetry_chain_detects_tampering():
    tel = spike.Telemetry()
    tel.append(actor="a", action="tool", target="x", payload="p")
    tel.append(actor="a", action="tool", target="y", payload="q")
    assert tel.verify()
    tel.records[0]["target"] = "z"
    assert not tel.verify()


def test_containment_is_fast_in_process():
    s = spike.run_all()["summary"]
    assert s["containment_ms_max"] < 50  # generous bound for shared CI runners
