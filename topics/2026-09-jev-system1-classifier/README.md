# Jev: a fast "System 1" classifier next to an LLM

**Ring: TRIAL** · Month: 2026-09 · Spike: [`spike.py`](spike.py) · Tests: [`tests/`](tests/README.md)

## What it is

Jev is a hosted choice API from TypeSafe AI. You send a piece of text plus the list of options it
could belong to; it returns the chosen option, a confidence, and a probability for every option.
There is no per-task training: the option list is the task definition.

The useful way to think about it is as a "System 1" (fast, cheap, reflexive) next to an LLM as
"System 2" (slow, expensive, deliberate). Most requests in a real workload are routine decisions
(which queue, which intent, which policy applies). A calibrated classifier can take those, and the
LLM only sees the cases where the classifier is unsure.

## Why it matters for enterprise

- **Cost and latency.** Routing, triage and intent detection are high-volume. Paying LLM prices
  for every one of them is the largest avoidable line in many agent budgets.
- **Predictable output.** A fixed option set cannot produce an off-list answer, which removes a
  class of parsing and validation failures.
- **Calibrated confidence is the control knob.** If the probabilities can be trusted, one
  threshold decides how much traffic escalates, so cost and quality become a setting, not a
  surprise.
- **Vendor risk.** It is a new, closed API; the architecture should let it be swapped for an
  in-house classifier without touching callers.

## What I tested

[`spike.py`](spike.py) builds a two-tier router for support tickets (billing / technical / sales):

1. **Data:** 900 synthetic tickets from a fixed seed (600 train, 300 test). About 1 in 5 has no
   class cue at all (only words every class uses) and about 1 in 3 also mentions another class's
   vocabulary, so the easy/hard split is realistic rather than trivially separable.
2. **Tier 1:** TF-IDF (unigrams + bigrams) + logistic regression via scikit-learn; if
   scikit-learn is missing, a multinomial Naive Bayes in numpy. Both sit behind a
   `ChoiceClassifier` interface that returns choice, confidence and per-option probabilities.
3. **Calibration check:** reliability bins (10 bins) and expected calibration error (ECE).
4. **Router:** confidence at or above a threshold keeps the tier-1 answer; below it the ticket
   goes to a **mock LLM**, set to be right on 96% of tickets (errors picked by a hash of the text,
   so runs are repeatable). The 96% is a parameter, not a measurement of any real model.
5. **Cost:** simulated unit prices of $0.00002 per tier-1 call and $0.0015 per LLM call.
6. **Jev adapter:** `JevChoiceAdapter` implements the same interface as a stub. It maps a
   response of that shape onto the `Choice` type, has no key, no endpoint and no HTTP client, and
   always raises if called. A test replaces `socket` to prove no network access happens.

## Results

From `python spike.py` (scikit-learn backend, the default when installed; CI installs it):

| Setup | Accuracy | Escalated to LLM | Simulated cost / 1k requests |
|---|---|---|---|
| Tier 1 only (logistic regression) | 0.870 | 0% | $0.020 |
| Two-tier, threshold 0.5 | 0.903 | 6.3% | $0.115 |
| Two-tier, threshold 0.6 | 0.943 | 12.7% | $0.210 |
| **Two-tier, threshold 0.7 (default)** | **0.970** | **16.7%** | **$0.270** |
| Two-tier, threshold 0.8 | 0.980 | 20.3% | $0.325 |
| Two-tier, threshold 0.9 | 0.973 | 30.7% | $0.480 |
| LLM only (mock, 96% setting) | 0.957 | 100% | $1.500 |

At threshold 0.7 the router costs **82% less** than sending everything to the LLM, and it scores
higher than LLM-only here because the confident tier-1 answers are almost all right. That second
point depends on the mock's error rate; with a stronger LLM it would be a tie, not a win.

**Calibration.** Logistic regression: ECE **0.085**. Confidence tracks accuracy well at the top
(0.9-1.0 bin: 208 tickets, 100% right) and is too optimistic in the middle (0.6-0.7 bin: mean
confidence 0.66, accuracy 0.17), which is exactly the band the threshold routes away.

**The fallback backend shows why calibration matters.** Naive Bayes: tier-1 accuracy 0.853 but
ECE **0.115**, and it is sure of itself even when wrong (272 of 300 tickets in the 0.9-1.0 bin at
92% accuracy). At threshold 0.7 it escalates only 4.0% and reaches 0.880; even at 0.9 it gets to
only 0.927. An overconfident System 1 quietly keeps the hard cases it should hand over.

Lesson for adopting Jev (or any classifier) as tier 1: measure calibration on your own labelled
traffic before choosing the threshold; accuracy alone does not tell you how the router will behave.

## Verdict: TRIAL

The two-tier pattern is clearly worth it; the spike shows large savings at equal or better
quality, provided confidence is calibrated. Jev itself stays in TRIAL until it has been measured on
real labelled data (calibration, latency, price, data-handling terms). The adapter interface means
the in-house classifier can ship first and Jev can be compared behind the same contract.

## Planned adoption

- A FinOps repo (planned, not yet published): tier-1 classification in front of LLM calls, with the
  threshold sweep and ECE reported as part of the eval gate.
- [Jagadish-azure-ai-integration-platform](https://github.com/jagadishmazure-jpg/Jagadish-azure-ai-integration-platform)
  request router: classify intent first, escalate to the agent only below the threshold.

Not adopted yet; this page will get an "Adopted into" link when it is.

## Sources

- Sebastian Raschka, [Language Models for Text Classification: From Bag-of-Words to Jev](https://magazine.sebastianraschka.com/p/classifier-history-and-jev) (Ahead of AI)

## Run it

```bash
python spike.py                    # scikit-learn backend if installed
python spike.py --backend numpy    # force the numpy Naive Bayes fallback
python spike.py --threshold 0.8
pytest -q tests
```
