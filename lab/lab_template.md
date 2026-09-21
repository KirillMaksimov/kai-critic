# Critic lab — template

**Copy this file into your own repository, not into the plugin.** The plugin ships
the empty shape; your lab holds your waves, your numbers and your hypotheses, and
it stays wherever your work lives. A plugin update replaces the plugin's own
directory — anything you keep here is destroyed by the next install.

Set the plugin's `lab_path` user config to the directory you copy it into, and
the skill will find it, pass it to the tool, and keep it out of every run's
allowed paths.

---

## What this file is

The half of the Critic's housekeeping the agent **never reads**. Its pair is the
desk, which the agent reads before every run.

| | Where | Why |
|---|---|---|
| **What we teach the agent** — lenses, techniques, stop rules, boundaries | the desk, read every run | the prior is the point |
| **What we measure the agent by** — ledger, precision, tics, hypotheses under test, verdicts | this file, never read | a prior here corrupts the measurement |

The lens ledger lives here for the same reason as the hypotheses, though it is not
one: a lens that reads "your precision is 0.67, you have a tic about measuring
reuse" starts suppressing findings not because they are wrong but because it read
that they are penalised. Goodhart on its own scoreboard.

**Never put this file in a run's allowed paths, and never inline it.**

---

## Main-thread protocol

*(Your own, accumulated. The skill carries the canonical version; this section is
for what your repository adds to it — the mistakes you have made merging, the
adjudications that turned out to matter.)*

---

## Lens ledger (keep/kill at the level of a lens)

*(One block per wave: what ran, under what limits, what came back, what it cost.
The numbers come from `tools/wave_stats.py stats <wave>` — do not retype them by
hand, and do not compute them by hand.)*

| Lens | Runs | Findings | Accepted | Verdict |
|---|---|---|---|---|
| **beneficiary** | | | | |
| **adversary** | | | | |
| **auditor** | | | | |

---

## Calibration history

*(One entry per wave, newest first or last — pick one and keep it. What the wave
taught about the method, not about the object.)*

---

## Hypotheses under test

What is **not yet proven** and therefore must not reach the desk: an agent that
reads a hypothesis stops being its test. A hypothesis moves to the desk only after
a run that never saw it confirms it.

| # | Hypothesis | Observations | Status |
|---|---|---|---|

**Rule of entry:** a hypothesis is recorded the moment it is noticed, and is
**never** restated in a run's task. The wave assigned to test it gets an ordinary
framing with no hint at all.

---

## Hypotheses journal — about the mechanism itself

Distinct from the section above: those are hypotheses about what the Critic finds
in other people's objects; these are about how the Critic itself should be run —
which model, how many runs, whether a stage pays.

**Two shapes, and they are tested differently** (skill step 0c):

- a **configuration** hypothesis — which model, how many runs, whether a stage is
  present — is an A/B on one object at `EFFORT: experimental`;
- a **charter or skill** hypothesis is not: the text also decides how much work
  the main thread does downstream, so two arms would differ by more than the
  factor. It is settled by landing the change and watching the ledger accumulate.

A hypothesis is confirmed or refuted by the owner **on the journal**, never by
the main thread on one wave. **Keep the numbering here separate from the section
above, or say plainly that it is separate** — two `H8`s in one file have already
cost one round of confusion.

| # | Hypothesis | How it is measured | Expected (written before) | Status |
|---|---|---|---|---|

---

## Ratification registry

*(One row per finding. The wave record in `waves/` is the source of truth, and
this is the human-readable face of it. Two tables, because the two blocks of the
review file are measured differently — skill §5, steps 2 and 3.)*

**The owner's block** — findings where ruling meant choosing what a person sees
or gets. His mark of usefulness and his decision, each beside the prediction that
was sealed before he saw the file.

| Wave | # | Lens | Sev | Predicted usefulness | His mark | Agreed | Predicted decision | His decision | Whose fix |
|---|---|---|---|---|---|---|---|---|---|

**The main thread's block** — findings it decided itself and showed as a row.
Silence is assent; a correction is an amendment or an overturn.

| Wave | # | Lens | Sev | What the main thread chose | His correction | Accepted / amended / overturned |
|---|---|---|---|---|---|---|

*(A lab that was kept before skill 0.9.0 has an older table here — prediction,
ruling, agreed, decision — from the time the first question was "is it true?".
Leave it as it is and start these two beneath it: the rows on either side of that
boundary answer different questions.)*
