---
name: kai-critic
description: Run the Critic over a design, a strategy or an instruction — three lenses in parallel, then merge and triage, with every finding ratified by the owner. Trigger when the user asks to criticise, review or pressure-test a proposal before committing to it — «прогони критика», «покритикуй дизайн», «что здесь не так», «дай адверсарий-взгляд», «run the critic», «/kai-critic» — when a past wave is to be ratified — «ратифицируем W11», «разбери находки прошлого прогона» — and whenever this session has produced a design or strategy that meets the calling threshold in §1. NOT for a finished deliverable whose recipient has already reacted, NOT for measuring a system that already runs, and NOT for code review (use /code-review).
---

# Critic — run protocol

You are the main thread. The Critic is a subagent (`kai-critic:kai-critic`);
this skill is the machinery around it.

**Step 0 — resolve the desk.** The agent reads a desk before it starts: the
accumulated craft, what has paid off, how this critic has gone wrong before.
Resolve it once, here, and pass the path in §3:

- configured desk: `${user_config.desk_path}`
- bundled generic desk: `${CLAUDE_PLUGIN_ROOT}/desk/desk_critic.md`

Use the configured one if that line names a file that exists; otherwise the
bundled one. If neither resolves, run on the charter alone and say so in one
line — the charter treats the desk as optional by design, and a repository
without one still gets a full run.

**Step 0b — read the lab** if this repository keeps one. A lab is the file that
carries the lens ledger, the open hypotheses and the calibration history; where
it lives is named in the repository's own instructions. It is optional
infrastructure — without it, run anyway and skip the ledger update in §6.

> **Never put the lab in a run's allowed paths, and never inline it.** It holds
> the hypotheses under test and the lens ledger; an agent that reads them stops
> being their test and starts playing to the scoreboard. The desk is the file
> the agent may read — it teaches how to look. The lab is what measures whether
> the looking worked, and it stays behind the agent's back.

## 1. Should this run at all?

Calling the Critic costs three passes and, more expensively, the owner's time
triaging what comes back. Run when **at least one** holds:

- the decision is hard to reverse once built;
- it is a new contour, not an edit to an existing one;
- the cost of being wrong is above the trivial (client delivery, money, data loss).

Otherwise say plainly that the threshold is not met and do not run. A tax on
every small design is the same negative value as an uncalibrated critic, just
from the other side.

## 2. Frame the run

| Field | How to set it |
|---|---|
| `OBJECT` | `design` (a system), `strategy` (a route to a goal), `instruction` (a skill, charter, contract — text an agent must act on) |
| `MODE` | **by whether reality exists yet**, not by object type. Nothing built, nothing to check against → `blind`. Implementation, history or a decisions log exists → `grounded` |
| Lenses | all three, always: `beneficiary`, `adversary`, `auditor` |

**`blind`:** the artifact and nothing else — inlined in the task message, or one
named path when it is large (verified cheaper by 3× and equally blind). Say
explicitly that no other file may be opened.

**`grounded`:** list the readable paths — the artifact, plus the neighbours where
a reader might find that an apparent gap is already closed. Also **name what is
unreachable** from this session (code in another repo, a generated artifact that
was never committed); the charter turns claims about those into `## Checks to run`
instead of findings.

Before launching: **snapshot the input** (copy it to a scratch directory, record
the commit). The calibration is prospective — the verdict arrives when reality
does, and the input must still be readable then.

## 3. Launch

Three `Agent` calls with `subagent_type: "kai-critic:kai-critic"` **in one
message**, so they run in parallel and blind to each other. Sequential runs let
the second anchor on the first and three seats collapse into one with an echo.

Identical prompts except `LENS:`. Each carries: `LENS` / `MODE` / `OBJECT`, the
problem the proposal must solve (written from the beneficiary's world, not the
author's), the proposal, the readable paths, the unreachable list, and the desk
path from step 0 — inlined instead of named when `MODE: blind`, so the
single-artifact rule still holds.

**Never hint at what they should find.** No hypothesis, no "check whether X", no
summary of previous runs' findings. That is the whole reason the lab is separate.

## 4. Merge — three jobs, not one

1. **Duplicates** — the same finding from two lenses *from different sides* goes
   up in severity, not into a merged blur.
2. **Chains** — adjacent links of one failure that look small alone. Seen once:
   "nothing makes her return the file" + "nobody can tell an abandoned session
   from a slow one" + "the accuracy report cannot tell a partial pass from a
   complete one" were three lenses holding three links, and no lens saw the whole.
   Look for these on purpose.
3. **Adjudicate facts** — when lenses cite different numbers or dates from the
   same corpus, check yourself. The real finding may be the discrepancy: one run
   turned up three different sizes for the same artifact, and no lens reported it.

**Read the neighbours' `## Out of lens` tails as carefully as their findings.**
A lens that correctly recognised something as not its seat and handed it over in
one line has done its job; the lens that owns that ground may never walk it. Seen
once: the auditor handed over a real high-severity contradiction, the adversary
never reached it, and it survived only because the tail was read. The separation
that produces chains produces this hole.

Then check whether an apparent **disagreement between lenses is real**. Twice out
of three it was not: the adversary's fixes were subtractive (name a population,
drop an unbacked claim, add one rule) and cost the beneficiary no ritual at all.
Only a genuine trade-off goes to the owner as a decision.

## 5. Triage — verify, then put every finding to the owner

**Manual ratification is the default.** Your verdict is a **prediction**, not a
decision. The owner rules on every finding, and the gap between his ruling and
yours is the measurement — without it, the precision in the ledger is your own
triage of an object you often wrote yourself. Turning this off is **his** call,
made on the evidence the ledger produces. Do not propose it because a wave went
well; a good wave under manual control is exactly the data that has never existed.

**Step 1 — verify.** Every checkable claim gets checked **by you** before it
reaches him. The `How to refute` line exists so this costs minutes. Run it.

**Step 2 — form your verdict and keep it to yourself.** Write it down — accepted
/ accepted with correction / downgraded / rejected, with the reason — *before*
you open the first dialog, so it cannot drift toward whatever he says.

**Step 3 — put each finding to him blind, one per dialog.** One
`AskUserQuestion` call, one finding. He sees:

- the finding as the lens wrote it — the problem, where, what breaks, severity;
- **the result of your check as a fact**: what the grep returned, what the
  arithmetic came to, what the file at that line actually says;
- nothing else.

Options: accept · accept with correction · downgrade severity · reject; he can
attach free text to any of them.

Two things stay hidden until step 4, for the same reason:

- **your verdict** — he anchors on it, and then the number measures whether he
  agrees with what you showed him. That is the Goodhart the lens-blindness rule
  in §3 exists to prevent, one seat further down. Facts inform; verdicts anchor.
- **which lens produced it** — the lenses carry reputations in the ledger, and a
  reputation is an anchor like any other.

**Never filter by your own confidence.** "Show him only the ones I am unsure
about" re-introduces precisely the bias under measurement.

**Step 4 — reveal, then record.** Once he has ruled on all of them, show one
table: finding · lens · your prediction · his ruling · agree?. Name the
disagreements plainly and do not argue them — a disagreement is a labelled
example, which is worth more than being right. Both numbers go to §6.

**Backdated ratification** (a wave triaged before this section existed) runs the
same way: read the findings out of that wave's review note, present them blind,
and do not show the verdicts already written there. **Enter the skill here** —
§§1–4 already happened, so do not re-run lenses; step 0b still applies, because
the lab is where the result goes and it names which wave is waiting.

## 6. Land it

- **Review note** in the owning project, wired into wherever that project lists
  its notes. Structure: what ran and under what limits · accepted findings by
  severity · accepted as questions · downgraded and rejected, with reasons ·
  inter-lens disagreement as a decision · what the run said about the Critic
  itself. Under manual ratification the **owner's ruling is the verdict of
  record**; yours is kept beside it as the prediction, not quietly replaced by his.
- **The lab** *(if the repository keeps one)*: lens ledger row, any new tic, any
  new hypothesis (never into the desk until a clean run confirms it), plus one
  **ratification row per finding**.
- **The desk** *(if the repository keeps its own)*: only techniques confirmed
  enough to teach. Never write to the bundled generic desk from a run — a plugin
  update overwrites it.
- **Land the outcomes** by whatever convention this repository uses for session
  outcomes.
- State the cost in tokens and **two** numbers, never one:
  - **precision** = his acceptances ÷ findings — an acceptance rather than your
    own triage;
  - **triage agreement** = the share where your prediction matched his ruling —
    the measured size of the authorship confound, and a number about *you*, not
    about the lenses.
  A low agreement with a high precision means the lenses are fine and your triage
  is not. Report it that way round; it is the more useful failure.

## 7. Two standing cautions

- **Agent definitions are snapshotted.** A charter edit does not reach a run that
  is already under way. If the charter changed this session, say so and treat the
  results as run against the previous version.
- **Edit the source, never the installed copy.** The charter that runs is the
  installed one; editing it in place is silently undone by the next update, and
  editing the source repository does not reach the installed copy until
  `claude plugin update kai-critic` and a restart. Change the source, bump the
  version, update, and only then trust that a run is testing the new text.
