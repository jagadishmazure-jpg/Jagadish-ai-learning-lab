"""Spike: a two-tier ("System 1 / System 2") router for support tickets.

Tier 1 is a cheap text classifier. If its top probability clears a threshold, its label is used;
otherwise the ticket escalates to tier 2, a mock LLM. The spike measures accuracy, the share of
traffic escalated, calibration (reliability bins and expected calibration error), and simulated
cost per 1,000 requests against sending everything to the LLM.

Tier 1 backend: TF-IDF + logistic regression (scikit-learn) when installed, otherwise a
multinomial Naive Bayes written in numpy. Force one with --backend {sklearn,numpy}.

The Jev adapter at the bottom is a stub behind the same interface. It never calls the network.

Everything is offline and deterministic: the dataset is generated from a fixed seed, and the
mock LLM's "mistakes" are chosen by a hash of the ticket text, not by randomness.

Run:  python spike.py [--backend numpy] [--threshold 0.7]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from dataclasses import dataclass
from typing import Protocol

import numpy as np

LABELS = ("billing", "technical", "sales")

# --------------------------------------------------------------------------- synthetic data

_VOCAB = {
    "billing": {
        "nouns": ["invoice", "charge", "refund", "payment", "receipt", "credit card", "bill"],
        "verbs": ["was charged twice", "need a refund", "cannot pay", "was overbilled"],
        "extras": ["last month", "on my statement", "for the annual plan", "after I cancelled"],
    },
    "technical": {
        "nouns": ["login", "dashboard", "API", "sync", "export", "mobile app", "password reset"],
        "verbs": ["keeps crashing", "returns an error", "is not loading", "times out"],
        "extras": ["since the update", "on Chrome", "for all users", "every few minutes"],
    },
    "sales": {
        "nouns": ["enterprise plan", "quote", "demo", "pricing tier", "volume discount", "trial"],
        "verbs": ["would like a", "want to compare", "are evaluating", "need details on"],
        "extras": ["for 200 seats", "before our budget review", "for next quarter", "for our team"],
    },
}
_FILLER = ["hi team", "hello", "quick question", "please help", "thanks in advance", ""]
# Words every class uses. A ticket made only of these carries no real signal.
_SHARED = [
    "my account",
    "our subscription",
    "the plan",
    "an upgrade",
    "the workspace",
    "my team",
    "the order",
    "this week",
    "the admin page",
    "our contract",
]
_GENERIC = ["i have a question about", "something is off with", "can someone look at", "need help with"]


def _ticket(rng: random.Random, label: str, p_cue: float, p_distractor: float) -> str:
    v = _VOCAB[label]
    parts = [rng.choice(_FILLER)]
    if rng.random() < p_cue:
        parts.append(f"the {rng.choice(v['nouns'])} {rng.choice(v['verbs'])}")
        if rng.random() < 0.5:
            parts.append(rng.choice(v["extras"]))
    else:
        parts.append(f"{rng.choice(_GENERIC)} {rng.choice(_SHARED)}")
    parts.append(rng.choice(_SHARED))
    if rng.random() < p_distractor:  # borrow a cue from another class
        other = _VOCAB[rng.choice([x for x in LABELS if x != label])]
        parts.append(f"and maybe the {rng.choice(other['nouns'])}")
    return " ".join(p for p in parts if p)


def make_dataset(n: int = 900, p_cue: float = 0.8, p_distractor: float = 0.35, seed: int = 7):
    """Deterministic synthetic tickets. About 1 in 5 has no class cue at all (only shared
    words), and about 1 in 3 also mentions another class's vocabulary as a distractor."""
    rng = random.Random(seed)
    rows = [(_ticket(rng, LABELS[i % 3], p_cue, p_distractor), LABELS[i % 3]) for i in range(n)]
    rng.shuffle(rows)
    return rows


# --------------------------------------------------------------------------- interface


@dataclass(frozen=True)
class Choice:
    choice: str
    confidence: float
    probabilities: dict[str, float]


class ChoiceClassifier(Protocol):
    def classify(self, text: str, options: tuple[str, ...]) -> Choice: ...


# --------------------------------------------------------------------------- tier 1 backends


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class NumpyNaiveBayes:
    """Multinomial Naive Bayes with Laplace smoothing over unigrams and bigrams."""

    name = "numpy-naive-bayes"

    def fit(self, texts: list[str], labels: list[str]) -> NumpyNaiveBayes:
        self.classes = sorted(set(labels))
        feats = [self._feats(t) for t in texts]
        self.vocab = {w: i for i, w in enumerate(sorted({w for f in feats for w in f}))}
        counts = np.ones((len(self.classes), len(self.vocab)))  # alpha = 1
        prior = np.zeros(len(self.classes))
        for f, y in zip(feats, labels, strict=True):
            c = self.classes.index(y)
            prior[c] += 1
            for w in f:
                counts[c, self.vocab[w]] += 1
        self.log_prior = np.log(prior / prior.sum())
        self.log_lik = np.log(counts / counts.sum(axis=1, keepdims=True))
        return self

    @staticmethod
    def _feats(text: str) -> list[str]:
        t = _tokens(text)
        return t + [f"{a}_{b}" for a, b in zip(t, t[1:], strict=False)]

    def predict_proba(self, texts: list[str]) -> np.ndarray:
        out = []
        for text in texts:
            idx = [self.vocab[w] for w in self._feats(text) if w in self.vocab]
            s = self.log_prior + self.log_lik[:, idx].sum(axis=1)
            s = np.exp(s - s.max())
            out.append(s / s.sum())
        return np.array(out)


class SklearnLogReg:
    name = "sklearn-tfidf-logreg"

    def fit(self, texts: list[str], labels: list[str]) -> SklearnLogReg:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression

        self.vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
        self.clf = LogisticRegression(max_iter=1000, C=4.0)
        self.clf.fit(self.vec.fit_transform(texts), labels)
        self.classes = list(self.clf.classes_)
        return self

    def predict_proba(self, texts: list[str]) -> np.ndarray:
        return self.clf.predict_proba(self.vec.transform(texts))


def make_backend(name: str = "auto"):
    if name in ("auto", "sklearn"):
        try:
            import sklearn  # noqa: F401

            return SklearnLogReg()
        except ImportError:
            if name == "sklearn":
                raise
    return NumpyNaiveBayes()


class LocalChoiceClassifier:
    """Wraps a trained backend so it answers like a choice API."""

    def __init__(self, model):
        self.model = model

    def classify(self, text: str, options: tuple[str, ...] = LABELS) -> Choice:
        p = self.model.predict_proba([text])[0]
        probs = {c: float(p[i]) for i, c in enumerate(self.model.classes) if c in options}
        total = sum(probs.values())
        probs = {k: v / total for k, v in probs.items()}
        best = max(probs, key=probs.get)
        return Choice(best, probs[best], probs)


# --------------------------------------------------------------------------- tier 2 (mock LLM)


class MockLLM:
    """Stand-in for an LLM call: right except on a fixed, hash-selected share of tickets.

    The error rate is a parameter, not a measurement of any real model.
    """

    def __init__(self, gold: dict[str, str], error_rate: float = 0.04):
        self.gold, self.error_rate, self.calls = gold, error_rate, 0

    def classify(self, text: str, options: tuple[str, ...] = LABELS) -> Choice:
        self.calls += 1
        truth = self.gold[text]
        h = int(hashlib.sha256(text.encode()).hexdigest(), 16)
        if (h % 10_000) / 10_000 < self.error_rate:
            wrong = [o for o in options if o != truth]
            truth = wrong[h % len(wrong)]
        return Choice(truth, 1.0, {o: float(o == truth) for o in options})


# --------------------------------------------------------------------------- metrics

# Simulated unit prices (USD per request). Assumptions for comparison only.
COST_TIER1 = 0.00002  # small CPU model
COST_LLM = 0.0015  # roughly a short prompt + short answer on a hosted LLM


def reliability(conf: np.ndarray, correct: np.ndarray, bins: int = 10):
    edges = np.linspace(0.0, 1.0, bins + 1)
    rows, ece = [], 0.0
    for lo, hi in zip(edges[:-1], edges[1:], strict=True):
        m = (conf > lo) & (conf <= hi)
        if not m.any():
            continue
        acc, avg = float(correct[m].mean()), float(conf[m].mean())
        ece += m.mean() * abs(acc - avg)
        rows.append({"bin": f"{lo:.1f}-{hi:.1f}", "n": int(m.sum()), "acc": acc, "conf": avg})
    return rows, float(ece)


def evaluate(backend: str = "auto", threshold: float = 0.7, seed: int = 7) -> dict:
    data = make_dataset(seed=seed)
    train, test = data[:600], data[600:]
    model = make_backend(backend).fit([t for t, _ in train], [y for _, y in train])
    tier1 = LocalChoiceClassifier(model)
    gold = {t: y for t, y in test}

    t1 = [tier1.classify(t) for t, _ in test]
    conf = np.array([c.confidence for c in t1])
    correct = np.array([c.choice == y for c, (_, y) in zip(t1, test, strict=True)])
    bins, ece = reliability(conf, correct)

    def route(th: float) -> dict:
        llm = MockLLM(gold)
        preds = [
            c.choice if c.confidence >= th else llm.classify(t).choice
            for c, (t, _) in zip(t1, test, strict=True)
        ]
        acc = float(np.mean([p == y for p, (_, y) in zip(preds, test, strict=True)]))
        esc = llm.calls / len(test)
        cost = 1000 * (COST_TIER1 + esc * COST_LLM)
        return {"threshold": th, "accuracy": acc, "escalated": esc, "cost_per_1k": cost}

    llm_only = MockLLM(gold)
    llm_acc = float(np.mean([llm_only.classify(t).choice == y for t, y in test]))
    return {
        "backend": model.name,
        "n_train": len(train),
        "n_test": len(test),
        "tier1_only_accuracy": float(correct.mean()),
        "ece": ece,
        "reliability": bins,
        "two_tier": route(threshold),
        "sweep": [route(th) for th in (0.5, 0.6, 0.7, 0.8, 0.9)],
        "llm_only": {"accuracy": llm_acc, "cost_per_1k": 1000 * COST_LLM},
    }


# --------------------------------------------------------------------------- Jev adapter (stub)


class JevNotConfigured(RuntimeError):
    pass


class JevChoiceAdapter:
    """Where a hosted choice API (Jev by TypeSafe AI) would plug in. Stub only.

    It shows the shape I would send (text + options) and the shape I expect back (choice,
    confidence, per-option probabilities), mapped onto the same Choice type. It has no key, no
    endpoint and no HTTP client; classify() always raises. The request shape is my assumption,
    not the vendor's documented schema.
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    @staticmethod
    def build_request(text: str, options: tuple[str, ...]) -> dict:
        return {"input": text, "options": list(options)}

    @staticmethod
    def parse_response(body: dict) -> Choice:
        probs = {k: float(v) for k, v in body["probabilities"].items()}
        return Choice(body["choice"], float(body["confidence"]), probs)

    def classify(self, text: str, options: tuple[str, ...] = LABELS) -> Choice:
        raise JevNotConfigured("stub: this spike never calls the real Jev API")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="auto", choices=["auto", "sklearn", "numpy"])
    ap.add_argument("--threshold", type=float, default=0.7)
    a = ap.parse_args()
    r = evaluate(a.backend, a.threshold)
    print(f"backend={r['backend']}  train={r['n_train']}  test={r['n_test']}")
    print(f"tier-1 only accuracy {r['tier1_only_accuracy']:.3f}   ECE {r['ece']:.3f}")
    print("reliability bins (confidence -> accuracy):")
    for b in r["reliability"]:
        print(f"  {b['bin']}  n={b['n']:3d}  conf={b['conf']:.2f}  acc={b['acc']:.2f}")
    print(f"{'threshold':>9} {'accuracy':>8} {'escalated':>9} {'$/1k':>7}")
    for s in r["sweep"]:
        print(f"{s['threshold']:9.1f} {s['accuracy']:8.3f} {s['escalated']:9.1%} {s['cost_per_1k']:7.3f}")
    lo = r["llm_only"]
    print(f"LLM only: accuracy {lo['accuracy']:.3f}, ${lo['cost_per_1k']:.3f} per 1k")
    print(json.dumps({"two_tier": r["two_tier"], "llm_only": lo}, indent=2))


if __name__ == "__main__":
    main()
