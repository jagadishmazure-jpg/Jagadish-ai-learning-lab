"""Documentation standard: the docs set, ADRs, component docs, ownership, no dates or placeholders,
and the test count in the root README."""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache"}
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


def _md():
    return [p for p in ROOT.rglob("*.md") if not SKIP & set(p.relative_to(ROOT).parts)]


def test_docs_set_exists():
    for name in (
        "best-practices.md",
        "implementation-guide.md",
        "adopt-this.md",
        "no-infrastructure.md",
        "adr/README.md",
        "components/README.md",
    ):
        assert (ROOT / "docs" / name).is_file(), name


def test_adrs_are_indexed_and_complete():
    index = (ROOT / "docs/adr/README.md").read_text()
    adrs = sorted((ROOT / "docs/adr").glob("0*.md"))
    assert len(adrs) >= 5
    for p in adrs:
        text = p.read_text()
        assert f"({p.name})" in index, p.name
        for part in ("**Status:**", "## Context", "## Decision", "## Consequences"):
            assert part in text, (p.name, part)


def test_component_docs_have_the_17_sections():
    docs = [p for p in (ROOT / "docs/components").glob("*.md") if p.name != "README.md"]
    assert docs
    for p in docs:
        assert re.findall(r"^## \d+\. (.+)$", p.read_text(), re.M) == SECTIONS, p.name


def test_codeowners_and_no_github_readme():
    assert "* @jagadishmazure-jpg" in (ROOT / ".github/CODEOWNERS").read_text()
    # GitHub would show .github/README.md instead of the root README on the repo page.
    assert not (ROOT / ".github/README.md").exists()


def test_ci_checks_doc_drift():
    assert "scripts/doc_drift.py --check" in (ROOT / ".github/workflows/ci.yml").read_text()


def test_no_placeholders_or_dates_in_docs():
    bad = []
    for p in _md():
        text = p.read_text()
        prose = re.sub(r"```.*?```|`[^`]*`", "", text, flags=re.S)
        if re.search(r"\b(TODO|TBD|FIXME)\b", prose):
            bad.append(f"{p.relative_to(ROOT)}: placeholder")
        if re.search(r"\b20\d\d-\d\d\b|\b(19|20)\d\d\b", prose):
            bad.append(f"{p.relative_to(ROOT)}: date or year")
    assert not bad, bad


def test_readme_test_count_matches_collection():
    out = subprocess.run(
        [sys.executable, "-m", "pytest", "--co", "-q", "-p", "no:cacheprovider"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    ).stdout
    # pyproject addopts already has -q, so this is -qq: one "path: count" line per test file
    n = sum(int(x) for x in re.findall(r"\.py: (\d+)$", out, re.M))
    m = re.search(r"(\d+) tests running in CI", (ROOT / "README.md").read_text())
    assert m and int(m.group(1)) == n, (m and m.group(1), n)


def test_workflows_are_hardened():
    """Supply-chain guard: every third-party action is pinned to a full commit SHA with a version
    comment, every workflow sets top-level permissions, CI runs gitleaks, and CodeQL and Dependabot
    are configured. Dependabot bumps keep the SHA and the comment together, so this stays green."""
    wf_dir = ROOT / ".github" / "workflows"
    for f in sorted(wf_dir.glob("*.yml")):
        text = f.read_text()
        assert re.search(r"^permissions:", text, re.M), f"{f.name}: no top-level permissions"
        for line in text.splitlines():
            m = re.search(r"\buses:\s*([^\s#]+)\s*(#.*)?$", line)
            if m and not m.group(1).startswith("./"):
                assert re.fullmatch(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}", m.group(1)), f"{f.name}: {line.strip()}"
                assert m.group(2) and re.match(r"#\s*v\d", m.group(2)), f"{f.name}: no version comment"
    assert "gitleaks/gitleaks-action@" in (wf_dir / "ci.yml").read_text()
    assert "github/codeql-action/analyze@" in (wf_dir / "codeql.yml").read_text()
    deps = (ROOT / ".github" / "dependabot.yml").read_text()
    assert "package-ecosystem: github-actions" in deps and "interval: weekly" in deps
