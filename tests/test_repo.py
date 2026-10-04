"""Repository rules: every topic is complete, listed on the radar and in the changelog, and every
folder explains itself with a README."""

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOPICS = sorted(p for p in (ROOT / "topics").iterdir() if p.is_dir() and not p.name.startswith("_"))
RINGS = {"ADOPT", "TRIAL", "ASSESS", "HOLD"}
SECTIONS = [
    "Purpose",
    "Architecture",
    "How it works",
    "Key files",
    "Code excerpts",
    "Configuration",
    "Commands",
    "Real output",
    "Tests and eval gates",
    "Guardrails",
    "Security and governance",
    "Observability",
    "Failure modes",
    "Mapping to Azure services",
    "Limitations",
    "Interview talking points",
    "Adopt this",
]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def radar() -> dict[str, str]:
    """{topic folder: ring} from the TECH RADAR table in the root README."""
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    section = text.split("## Tech radar", 1)[1].split("\n## ", 1)[0]
    rows = re.findall(r"^\|\s*\*\*(\w+)\*\*\s*\|\s*\[[^\]]+\]\(topics/([^/)]+)/?\)", section, re.M)
    return {folder: ring for ring, folder in rows}


def test_there_are_topics():
    assert len(TOPICS) >= 4


@pytest.mark.parametrize("topic", TOPICS, ids=lambda p: p.name)
def test_topic_layout(topic):
    assert re.fullmatch(r"\d{2}-[a-z0-9]+(-[a-z0-9]+)*", topic.name)
    for f in ("README.md", "spike.py", "tests/README.md"):
        assert (topic / f).is_file(), f"{topic.name} is missing {f}"
    assert list((topic / "tests").glob("test_*.py")), f"{topic.name} has no tests"


@pytest.mark.parametrize("topic", TOPICS, ids=lambda p: p.name)
def test_topic_readme_sections_and_ring(topic):
    text = (topic / "README.md").read_text(encoding="utf-8")
    heads = re.findall(r"^## \d+\. (.+)$", text, re.M)
    assert heads == SECTIONS, f"{topic.name}: sections {heads}"
    assert "```mermaid" in text and "<!-- output:" in text and "<!-- code:" in text
    m = re.search(r"^\*\*Ring: (\w+)\*\*", text, re.M)
    assert m and m.group(1) in RINGS
    assert f"### Verdict: {m.group(1)}" in text, "verdict heading must match the ring"
    if m.group(1) == "ADOPT":
        adopted = text.split("### Adopted into", 1)
        assert len(adopted) == 2 and "](https://github.com/" in adopted[1].split("\n### ")[0]
    sources = text.split("## Sources", 1)[1].split("\n## ")[0]
    assert "](http" in sources or "YouTube" in sources, "sources need a link (or a named video)"


def test_radar_lists_every_topic_with_matching_ring():
    r = radar()
    assert set(r) == {t.name for t in TOPICS}
    for t in TOPICS:
        ring = re.search(r"^\*\*Ring: (\w+)\*\*", (t / "README.md").read_text(), re.M).group(1)
        assert r[t.name] == ring, f"{t.name}: radar says {r[t.name]}, page says {ring}"


def test_changelog_mentions_every_topic():
    log = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    for t in TOPICS:
        assert t.name in log, f"{t.name} has no CHANGELOG entry"


def test_every_folder_has_a_readme():
    files = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    folders = {Path(f).parent for f in files}
    # .github is skipped on purpose: GitHub would show .github/README.md instead of the root README
    missing = [
        str(d) for d in folders if not str(d).startswith(".") and not (ROOT / d / "README.md").is_file()
    ]
    assert not missing, f"folders without README.md: {missing}"


def test_new_topic_script(tmp_path):
    (tmp_path / "topics").mkdir()
    import shutil

    shutil.copytree(ROOT / "TEMPLATE", tmp_path / "TEMPLATE")
    mod = _load(ROOT / "scripts" / "new_topic.py", "new_topic_script")
    dest = mod.create("demo-tool", "Demo Tool", root=tmp_path)
    assert dest.name == "01-demo-tool"
    text = (dest / "README.md").read_text()
    assert text.startswith("# Demo Tool") and "{{" not in text
    assert (dest / "spike.py").is_file() and (dest / "tests" / "test_spike.py").is_file()
    assert mod.create("other-tool", "Other", root=tmp_path).name == "02-other-tool"
    with pytest.raises(ValueError):
        mod.create("Bad Slug", "X", root=tmp_path)
    with pytest.raises(FileExistsError):
        mod.create("demo-tool", "Demo Tool", root=tmp_path)


def test_link_checker_local_rules(tmp_path):
    mod = _load(ROOT / "scripts" / "check_links.py", "check_links_script")
    assert mod.slug("Verdict: ADOPT") == "verdict-adopt"
    assert mod.slug("At a glance (for recruiters)") == "at-a-glance-for-recruiters"
    md = ROOT / "README.md"
    assert mod.check_local(md, "CHANGELOG.md") is None
    assert mod.check_local(md, "does-not-exist.md")
    assert mod.check_local(md, "#tech-radar") is None
    assert mod.check_local(md, "#no-such-heading")


def test_no_network_calls_in_spikes():
    for t in TOPICS:
        src = (t / "spike.py").read_text(encoding="utf-8")
        for bad in ("import requests", "import httpx", "urllib.request", "import openai"):
            assert bad not in src, f"{t.name} spike must stay offline ({bad})"
