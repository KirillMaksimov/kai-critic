---
name: kai-critic
description: Run the Critic over a design, a strategy or an instruction — three lenses in parallel, then merge, verify, and write every finding into a review file the owner rules on. Trigger ONLY when the user asks for it by name — «прогони критика», «покритикуй дизайн», «что здесь не так», «дай адверсарий-взгляд», «run the critic», «/kai-critic» — or when a past wave is to be ratified — «ратифицируем W11», «разбери находки прошлого прогона». Never launch it because a session has just produced a design (§1). NOT for a finished deliverable whose recipient has already reacted, NOT for measuring a system that already runs, and NOT for code review (use /code-review).
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

**Step 0b — read the lab** if there is one. A lab carries the lens ledger, the
open hypotheses and the calibration history. It lives in **the owner's own
repository**, never in this plugin: it holds their objects and their rulings, and
a plugin update would destroy anything kept here. Resolve it once:

- configured lab directory: `${user_config.lab_path}`
- otherwise, whatever the repository's own instructions name

It is optional infrastructure — without one, run anyway and skip the ledger
update in §6. To start one, `${CLAUDE_PLUGIN_ROOT}/lab/lab_template.md` is the
empty shape and `${CLAUDE_PLUGIN_ROOT}/lab/README.md` says how to wire it up;
offer that, never create it unasked.

**When a lab directory is configured, its numbers are computed, never counted.**
`${CLAUDE_PLUGIN_ROOT}/tools/wave_stats.py` owns every deterministic figure the
protocol asks for — the four counts, the main thread's ratios, per-run and
per-lens yield, topic overlaps, the cross-wave medians. You supply the judgment it cannot
make (which findings are one topic, which refutation held) as one wave record;
it supplies the arithmetic. Counting any of it by hand re-introduces exactly the
error the layer exists to prevent, and the mistake does not raise — it prints a
plausible number.

> **Never put the lab in a run's allowed paths, and never inline it.** It holds
> the hypotheses under test and the lens ledger; an agent that reads them stops
> being their test and starts playing to the scoreboard. The desk is the file
> the agent may read — it teaches how to look. The lab is what measures whether
> the looking worked, and it stays behind the agent's back.

**Step 0c — read the lab's hypotheses journal**, if the lab keeps one. It lists
what is currently believed about the mechanism itself — which model, how many
runs, whether a topic pass pays — and how each belief is to be measured. If a
hypothesis names a configuration this run could test at a cost the owner might
accept, **offer it**: this run at `EFFORT: experimental` under that hypothesis,
with the cost stated. Never fold a hypothesis into a run without the owner's
yes, and never tell the lenses a hypothesis exists — the lab stays behind their
back for exactly this reason.

**Not every hypothesis is an A/B, and offering the wrong shape wastes a wave.**
A hypothesis about a **configuration** — which model, how many runs, whether a
stage is present — is settled by two arms on one object, and that is what
`EFFORT: experimental` exists for. A hypothesis about the **charter or this
skill** is not: writing the change into one arm and not the other makes the arms
differ by more than the factor, because the text also decides how much work the
main thread does downstream, and nothing can then be attributed. Such a
hypothesis is settled by landing the change and watching the ledger accumulate
across ordinary waves — so what it needs from a run is not a configuration but a
number recorded every time. Offer the shape that fits, and say which it is.

**A charter or skill change invalidates comparison with every wave before it —
each for its own numbers.** The charter decides what the lenses return, so a
charter change cuts the lens-side numbers: raw findings, topics, unique topics,
and everything computed from them. This skill decides what the owner is asked and
how his answers are counted, so a skill change cuts the main thread's ratios —
and, as long as it leaves framing, launch and merge (§§2–4) alone, **nothing
lens-side**: the median of unique topics per lens runs on through it. After a
change, that side's numbers may be compared with waves under the same text, and
with the other arm of its own run, but never with a baseline from earlier — the
journal quotes those baselines by name, and a later session reading them has no
way to see that the text moved. When it applies, say so in the ledger row and in
the journal entry that owns the baseline. The wave record names both versions
(§6) for exactly this reason, and the tool keeps the two sides of a skill change
in separate tables rather than in one column.

## 1. Who starts a run

**The owner starts it, and nothing else does.** The skill runs when he asks for
it — by name, by `/kai-critic`, or in his own words. It does **not** run because
this session has just produced a design, because an object looks new or hard to
reverse, or because some threshold appears to be met. A session that finishes a
design says what it finished and stops there; whether the critic gets a seat is
his call, and he makes it with the cost in front of him.

That cost, so the number is available when he asks what a run would take: a
topic pass plus three lens passes, around a million subagent tokens on a
grounded design of ordinary size, and — the expensive half — his own attention
ruling on what comes back.

You may say **once**, in one line, that the object looks small and reversible,
or that one of the classes below fits it better. Say it once and run anyway if
he still wants the run: a second unasked opinion about his priorities is a tax
of exactly the kind this section used to impose.

Where another instrument fits better:

- **a finished deliverable whose recipient has already reacted** — reality
  arrived, so the question is "did it work", not "will it";
- **a system that already runs** — that needs an evaluation pipeline, one per
  system, with no agent in the loop;
- **code review** — a different instrument with different failure modes
  (`/code-review`).

## 2. Frame the run

| Field | How to set it |
|---|---|
| `OBJECT` | `design` (a system), `strategy` (a route to a goal), `instruction` (a skill, charter, contract — text an agent must act on) |
| `MODE` | **by whether reality exists yet**, not by object type. Nothing built, nothing to check against → `blind`. Implementation, history or a decisions log exists → `grounded` |
| Lenses | all three, always: `beneficiary`, `adversary`, `auditor` |
| `EFFORT` | `normal` — the default: one topic pass on Opus, then one run per lens on Sonnet. `enhanced` — one topic pass on Opus, then two runs per lens on Sonnet in the same batch, and a third run offered per lens by saturation (§4). `experimental` — the configuration a hypothesis under test prescribes, run as an A/B on one object (§3). The owner picks; never escalate on your own |
| `SHAPE` | one sentence: how the object changes the shape of what it replaces ("a self-contained file becomes a long-lived local service"). Passed to every lens verbatim. Omit when nothing is replaced — the lens then derives it |
| Topic pass | on in `normal` and `enhanced`: `kai-critic:kai-topics` runs first and its merged list reaches every lens as `TOPICS:`. Off only as an experimental arm — whether the pass pays is answered by an arm that runs without it, never by switching it off quietly |

**`blind`:** the artifact and nothing else — inlined in the task message, or one
named path when it is large. Say explicitly that no other file may be opened.

A named path is only blind when **nothing attaches to it**. Your host may hand the
lens the standing instructions of the directory a file sits in — a `CLAUDE.md` or
its equivalent — simply because the lens read that file, without anyone listing
it. In this mode those are the author's own reasoning, which is precisely what the
mode exists to keep out. So if anything would attach, inline the artifact instead:
the single-path form was measured cheaper by 3× on artifacts with nothing above
them, and that measurement does not carry to a path inside an instrumented
repository.

**`grounded`:** list the readable paths — the artifact, plus the neighbours where
a reader might find that an apparent gap is already closed. Also **name what is
unreachable** from this session (code in another repo, a generated artifact that
was never committed); the charter turns claims about those into `## Checks to run`
instead of findings.

**Then enumerate what the host will attach on its own, and put it in the same
list.** For every path you name, the standing instructions of that directory and
of the directories above it reach the lens whether you list them or not. Reading
them is usually right: when the object under review is a repository's own
machinery — a skill, a plugin, a pipeline — its instructions are part of what is
being judged. What is not right is a record that says ten paths when the lens read
twelve. The wave cannot be reproduced, and the next run cannot be framed the same
way on purpose. List them, and the record matches what happened.

Before launching: **snapshot the input** (copy it to a scratch directory, record
the commit). The calibration is prospective — the verdict arrives when reality
does, and the input must still be readable then.

## 3. Launch

`Agent` calls with `subagent_type: "kai-critic:kai-critic"` **in one message**,
so they run in parallel and blind to each other. Sequential runs let the second
anchor on the first and three seats collapse into one with an echo. How many
calls is set by `EFFORT`:

- **`normal`** — one topic-pass call on Opus, then three lens calls, one per
  lens, on Sonnet. About a million subagent tokens on a grounded design of
  ordinary size. Subagent cost barely moves with the cap gone — a lens pays for
  reading, not for writing — but **your own** cost does: more findings to merge,
  more refutations to run, a longer pile in your context. The token line the
  owner sees should say which of the two grew.
- **`enhanced`** — one topic-pass call on Opus, then six lens calls, two per
  lens, byte-identical prompts within a lens (nothing distinguishes run 1 from
  run 2 except its result). After the
  merge (§4) look at each lens on its own: if its second run added at least
  one topic to what its first run found, **offer** the owner a third run of
  that lens, with its cost; a lens whose second run added nothing has
  saturated and is not offered. The third run is never launched unasked.
- **`experimental`** — an A/B on one object: two configurations that differ in
  **exactly one factor** — the model of a lens, the model of the topic pass,
  the presence of the topic pass, one sweep question switched off, grouped
  reading (`READS: batch` in one arm's lens prompts, both arms fed from one
  topic pass) — same
  object, same paths, same day, compared at topic level (§4). The hypothesis in
  the lab names the factor and the measure; the run record names the arm each
  agent belonged to. One factor, or the result cannot be attributed.

**Models.** Both charters default to Sonnet. `normal` and `enhanced` alike lift
the topic pass to Opus through the `Agent` tool's `model` parameter. That was
measured, not assumed: on one object, one Opus topic pass against one Sonnet
topic pass, with the same Sonnet lenses behind each, the Sonnet list was half as
long and the lenses working from it came back with a small fraction of what the
same lenses found from the Opus list — for barely fewer tokens. The list does not
only widen the floor; it pulls the lenses further. The owner took Opus as the
topic pass of every level on that evidence. An experimental arm may still
override either agent the same way. The auditor never goes below Sonnet —
it is an existential check, the class where a cheap tier has produced false
negatives before.

**Order of launch.** The topic pass goes first — `subagent_type:
"kai-critic:kai-topics"`, the same problem statement, proposal, paths,
unreachable list, `SHAPE:` and desk path as a lens would get; one call, two
only when a hypothesis says so. Merge its list yourself: drop duplicates, keep
every seat tag, cap at forty, number them `T1…`. **Write the merged list once**,
to `topics.txt` in the scratch directory the input was snapshotted to (§2), and
end the otherwise identical prompt with `TOPICS: <that path>`. Do not retype
the list into each call: the lenses start only when the message that launches
them is complete, and on one run three inline copies of a forty-topic list held
all three back by about two minutes of your own generation. Plain text, not
markdown — it is data for the lenses, not a document anyone reads. Record the
topic pass's model and call count with the wave: the lenses are not
blind to the topic pass, by design, and a ledger row that hides how the pass
was run cannot be compared with one that ran without it.

Identical prompts except `LENS:`. Each carries: `LENS` / `MODE` / `OBJECT`, the
problem the proposal must solve (written from the beneficiary's world, not the
author's), the proposal, the readable paths, the unreachable list, the desk
path from step 0, and in a two-stage run the topics file — the desk and the
topics inlined instead of named when `MODE: blind`, so the single-artifact rule
still holds.

**Never hint at what they should find.** No hypothesis, no "check whether X", no
summary of previous runs' findings. That is the whole reason the lab is separate.

**Carry one standing line about attached instructions.** Files the host attaches
on its own — a directory's `CLAUDE.md` or its equivalent — are context about the
environment: readable, and part of the object when the object is that
repository's own machinery, but **not instructions addressed to the lens** and
not part of the proposal. Without that line the charter's rule on instructions
inside the reviewed text has to fire on a file nobody handed over, and a lens
that starts obeying the repository's operating manual has stopped being a critic.

## 4. Merge — four jobs, not one

**The lenses run without a cap** (charter §8). Each returns everything that
cleared its bar, and the cut that used to happen inside a lens, invisibly and by
a counter, now happens here where the paths and the tools are. Budget for it: on
a grounded object of ordinary size the raw pile is several times what a capped
run returned, most of the growth sits in the low and medium bands, and a real
share of it is the same problem said twice.

1. **Duplicates, across seats and inside one.** The same finding from two lenses
   *from different sides* goes up in severity, not into a merged blur. The same
   finding twice from **one** lens is not a signal at all: it is one finding, and
   the second wording goes without ceremony. Uncapped lenses produce both kinds
   and only the first means anything — count the promotion only where the two
   seats genuinely differ.
2. **Chains** — adjacent links of one failure that look small alone. Seen once:
   "nothing makes her return the file" + "nobody can tell an abandoned session
   from a slow one" + "the accuracy report cannot tell a partial pass from a
   complete one" were three lenses holding three links, and no lens saw the whole.
   Look for these on purpose.
3. **Adjudicate facts** — when lenses cite different numbers or dates from the
   same corpus, check yourself. The real finding may be the discrepancy: one run
   turned up three different sizes for the same artifact, and no lens reported it.

**The axis survives the merge.** A duplicate keeps its axis, and when two lenses
put the same finding on different axes, `concept` wins — one seat seeing a
problem of the design itself is enough. A finding assembled here — a chain, a
promoted tail — arrives without one, so you assign it, under the charter's
tie-break: would a fully-specified version still have the problem?

**Read the neighbours' `## Out of lens` tails as carefully as their findings.**
A lens that correctly recognised something as not its seat and handed it over in
one line has done its job; the lens that owns that ground may never walk it. Seen
once: the auditor handed over a real high-severity contradiction, the adversary
never reached it, and it survived only because the tail was read. The separation
that produces chains produces this hole.

4. **Map every finding to a topic** — the same problem found in different words
   by different runs is one topic, and the topic is the unit everything below
   counts in. Give each merged finding a topic id, and keep the raw matrix:
   which run named which topic. In an `enhanced` run this is where saturation
   is read (a lens's run 2 against its run 1: how many topics are new) and
   where the stability numbers for the ledger come from — topics per run, the
   union, the share of topics found by every run of a lens, pairwise overlap.
   In an `experimental` run it is the comparison between the arms. If the owner
   wants to see the divergence picture before ruling, show it with the runs
   numbered and the lenses hidden: a topic without a seat is exactly what the
   merge produces, and the seat is one of the three anchors §5 keeps back.

Then check whether an apparent **disagreement between lenses is real**. Twice out
of three it was not: the adversary's fixes were subtractive (name a population,
drop an unbacked claim, add one rule) and cost the beneficiary no ritual at all.
Only a genuine trade-off goes to the owner as a decision.

## 5. Triage — verify, then write the review file

**Manual ratification is the default.** Your verdict is a **prediction**, not a
decision. The owner rules on every finding that is his to rule on — step 2 draws
that line, and step 3 shows him the rest — and the gap between his answer and your
prediction is the measurement: without it, the usefulness in the ledger is your
own opinion of an object you often wrote yourself. Turning this off is **his** call,
made on the evidence the ledger produces. Do not propose it because a wave went
well; a good wave under manual control is exactly the data that has never existed.

**He rules in a file, not in a dialog.** Everything that survives verification is
written into one review file, in full, and he answers it at his own pace — by
commenting in the file or by a list in chat, whichever suits him in the moment.
Nothing is put to him one finding at a time: a wave of twenty findings asked one
by one spends his evening on the dialog rather than on the findings, and the two
waves ratified by file comment (W18, W20) cost him a fraction of that with the
same rulings coming back.

**Step 1 — verify, and keep the trace.** Every checkable claim gets checked **by
you** before it reaches him. The `How to refute` line exists so this costs
minutes. Run it.

Where the finding is about **behaviour**, the check has to end in a
**reproduction** — from creating the object to the wrong result: the input, the
call, what came out, and what should have come out. That trace is what the
finding rests on in step 3 — he is told the fact in his own terms, and the trace
stays beside it as its address — and it is worth more than the lens's description
of it, because the description is the part that can be wrong.

Where the finding is about **absence** — a dimension the proposal never addresses
— there is nothing to run, and inventing a trace would be manufacturing evidence.
There the check is the fact as it stands: what the search returned, what the file
says at that line, which section does not exist.

**Only a refutation removes a finding, and the removal is shown.** With no cap on
the lenses, discarding what verification kills is your job and it is the reason
the cap could be lifted at all. It is also the one place where you can quietly
delete the measurement, so the rule is narrow:

- **A finding goes out when you ran its refutation and the refutation held** —
  the file says otherwise, the search returned what would void it, the mechanism
  it names is already there. That is a fact you can put on a line, and the line
  is what justifies the removal.
- **Nothing else takes one out.** Not low confidence, not "this is small", not
  "he will reject it", not "this is out of scope for the object". Those are
  rulings, and rulings are his — cutting by your own guess at his answer
  re-introduces exactly the bias manual ratification exists to measure, one step
  earlier than step 3, where nobody can see it.
- **Everything you removed goes to him in one block at the top of the review
  file** — one line each: the finding's own title, and what refuted it. A list he
  can scan in a minute and pull any row back from; a pulled-back row is
  renumbered into the body as a normal finding.

**Verify in severity order, high first, and mark what you could not settle.** A
low-severity finding whose refutation would cost an hour goes to him labelled
`not verified — <what it would take>`, which is a fact like any other. Chasing it
is worse than saying so, and dropping it for being expensive is the cut this rule
forbids.

**Keep the four counts** — raw findings from the lenses, what survived
deduplication, what your refutations removed, what he actually saw. They are the
only record of what the removed cap bought and what it cost (§6).

**Step 2 — sort by who decides, then form both predictions and keep them to
yourself.**

**Sort first — two levels, two blocks.** He decides what the system does for a
person; how it is built is yours. So before anything is predicted or written,
each finding that survived step 1 is placed by the level its decision lives on.

- **Requirement level** — what a person observes and gets: behaviour on the
  screens, the facts shown and how fresh they are, space on disk, load on the
  network and the machine, his own time and attention.
- **Specification level** — how the system is built so that a requirement holds:
  queues, locks, processes, tables, logs, classes, the order of steps inside a
  script.

A finding goes to **his block** when ruling on it means choosing what a person
will see or get: a requirement is missing; two requirements collide; the
proposal breaks a requirement he has already set, and the ways out differ in what
the person ends up with; a sensible fix cuts a feature; or the sensible fixes
differ in cost by an order he would want to know about — a rebuild against a
patch is his money. It goes to **your block** when every sensible fix gives
the person the same thing and the fixes differ only in mechanism.

**The working test: write the scenario first.** If you cannot say what a person
would see or get differently between the options, the choice is yours. If you are
unsure, it is his — and still written in his terms; doubt is never a licence to
hand him the mechanism.

**Sorting is not a filter.** Every finding that survived step 1 appears in the
file, in one block or the other; your block is shown to him row by row, and any
row is his to correct or to take back. What step 1 forbids — cutting by your own
guess at his answer — stays forbidden: sorting decides who answers, never whether
a finding is seen.

**Then predict.** Write both predictions into the
sealed file of step 3 **before the review file exists on disk**, so neither can
drift toward whatever he says. The order is not pedantry: on W14 he began
answering the moment the note appeared, a prediction had not been written yet,
and that finding had to be dropped from the measurement rather than "predicted"
after the fact. Predictions first, note second, always. They are made only for
the findings that go to **his** block:

- **how useful he will find it** — it changed a decision / it extended one / it
  refined one / noise, on the four definitions of step 3;
- **what he will do** — take one of your proposed fixes, write his own, hand the
  choice to you, not fix, move it into a task, or wait until he can see the thing.

Findings in your own block get no prediction: what is measured there is direct —
whether your decision stood.

The second is the more uncomfortable one. It measures whether you offer the moves
he actually wants, and the failure it catches is a standing one: an agent proposes
the repair it can write, which is almost always the local one.

**A finding about a channel outside the object — diagnostics, backup,
delivery, monitoring, security — is predicted as "into a task", not as one of
your fixes.** Measured three waves running: the owner agrees with such a finding
and moves it to work he has already planned, and the main thread, having noticed
the pattern in the aggregate, still predicts a plain repair row by row. Predict
the deferral.

**Before predicting one of your own letters, ask whether the finding opens a
decision or closes one.** A finding that names a defect with one obvious repair
closes the topic, and he usually takes the repair as written. A finding that
exposes a fork — where the thing should live, who owns it, which of two contours
it belongs to — is where he writes **his own**, because the owner supplies the
half the lens could not: the choice. Predicting one of your letters on a
fork-shaped finding is the single most repeatable triage error measured so far:
on one wave every miss was this shape — twice the owner added a decision the
finding had not contained (deliver it as its own repository, put the layer above
the mechanisms rather than inside each), once he lowered the cost instead of
taking it flat. When the lenses look fine and the agreement is low, the triage is
what failed; read it that way round, and look for the fork before you write the
prediction.

**Step 3 — write the review file: every finding at once, blind, in the owner's
terms.**

**The reader will not open the code, and should not have to.** He decides what
the system does for a person; how it is built is yours. So the file speaks in
what a person does, sees and gets, and it puts to him only the decisions that are
his: the two blocks of step 2 become the two blocks of the file, and every line
he reads is written as **scenario and effect**. The lenses are not
part of this — they write in the language of the object, with addresses in the
code, and they should. The translation is yours, and this step is where it
happens.

**His block — "your decisions".** The axis sets the order inside it — `concept`
findings first, by severity, because the owner's thinking is what they exist to
buy; `detail` findings after them, because the tail should cost him minutes
rather than attention. Each finding is **numbered** (`N1`, `N2`, … — a real id,
one sequence through both blocks, so a whole ruling fits in a line: "N7 —
changed a decision, fix b"). Each entry carries, in this order:

1. **The title — the effect, in one line a person would say**: "after the
   rebuild, the Refresh-all button does nothing for hours" — not the name of the
   component that causes it.
2. **Scenario → effect → stake**: who does what → what they see or get that is
   wrong → what it threatens. When the finding is a sequence, write it as steps
   with actors — who sent what to whom and what came back — because a conclusion
   shown without its path can be believed but not judged.
3. **Internal names only as an address** — in parentheses, after the phrase that
   has already said it in plain words: "the job that refreshes the prices
   (`price_sync.py`)". Never as the subject of a sentence. The check is
   mechanical: strike every parenthesis and every code span, and the entry must
   still read whole. Seen once: a finding whose effect for a person was real and
   was in the text — a button that would sit idle for hours — reached the owner
   under the names of two phases of a script and three mechanisms to choose
   from. He understood none of it, said so, and answered with a requirement for
   the button instead; the finding was useful and its form nearly killed it.
4. **A name the object coined that is also an ordinary word is the dangerous
   kind.** A priority class called "explicit" reads as "explicitly set", and the
   reader then doubts a finding that was verified. Describe the thing instead of
   naming it; if the name must appear, quote it and say once what it is.
5. **Severity and axis.** The axis is shown — it is the lens's claim about where
   the problem lives, the same kind of fact as severity, not a verdict.
6. **Verified — stated as a fact, never asked.** One sentence in his terms saying
   what you checked and what came back, then the trace from step 1 under it as
   the address for whoever wants it. Whether a finding is true was your job and
   step 1 did it; asking him re-opens a question he has no means to answer short
   of reading the code. A finding you could not settle says so: `not verified —
   <what it would take>`.
7. **The fixes you judge sensible**, one to three, lettered `a` / `b` / `c` so he
   can name one in a word — each written as **what changes for the person, and
   what it costs** (time to build, what is lost, what risk stays), the mechanism
   in parentheses if at all. "b) the button asks every collector to start now;
   the separate night sequence goes away (half a day)" — not "b) drop phases A
   and C of the chain".
8. **Two empty answer slots**, one per question below, for him to fill in place —
   **each with its allowed answers right beside it, in parentheses and in
   italics**, in the file's language: `**Was it useful?** *(changed a decision ·
   extended one · refined one · noise)*` and `**What do we do?** *(a · b · c ·
   don't fix · into a task: which · when I see it · your choice · your own, in
   words)*`, listing the letters this entry actually offers. He does not carry
   the scale in his head from one wave to the next, and should not have to.
   Seen twice running: with bare slots, he rated usefulness in his own words
   ("very useful", "medium", "low"), the main thread mapped them onto the scale,
   and on two waves the usefulness number held the main thread's judgement
   rather than his mark.
9. Nothing else.

| Question | Options |
|---|---|
| **Was it useful?** | it changed a decision · it extended one · it refined one · noise |
| **What do we do?** | your proposed fixes, one to three · don't fix · **into a task** · **when I see it** · **your choice** · his own, in free text |

**Was it useful — not "is it true".** An owner who does not read the code answers
"is it true" with "you checked, so yes", and leaves the slot empty; the ratio
built on those answers saturates and measures your verification, not the lenses.
Usefulness is the question only he can answer, and the one that tells one version
of the critic from another. The four ranks are the owner's own definitions:

- **It changed a decision** — a decision the design had taken is different
  after this finding.
- **It extended one** — the design stands as it was, but something is added: a
  new feature, or what a person sees and gets now reaches further.
- **It refined one** — a small precision that changes nothing a person observes.
- **Noise** — an unimportant finding that does not affect the delivery.

The second rank is the newest. Under three ranks a finding that added to a design
without reversing anything had nowhere to go, so it read as "changed a decision"
— and the headline share counted additions as reversals.

**Into a task.** A finding can be real, useful, and belong to work the owner
has already planned or will plan — a backup, a delivery channel, a security
pass — rather than to this object. That is a ruling of its own, not a rejected
finding and not a fix. The entry's second question therefore names a slot for
**which task** — an existing one from his task tree, or a new one he names; if
he chooses "into a task" without naming one, that is a gap, and gaps are asked
together at the end rather than one at a time. The lenses never learn this class
exists; they keep finding such things, and it is the main thread's job to carry
each one into the task it belongs to (§6).

**When I see it.** Some findings cannot be judged on paper — whether a screen
carries too much is a thing he will know when he looks at it. That is a ruling
of its own: not an acceptance, not a rejection, and not a lowered severity. The
object is built as designed, the finding stays open, and §6 carries it to where
the showing will happen.

**Your choice.** He may hand any decision back. That is a datum about your
sorting — the finding belonged in your block — and never a hit for whichever fix
you then pick (§6).

**Your block — "decided by the main thread".** One row per finding, numbered in
the same sequence:

- the effect for a person, in one phrase — or, plainly, that nothing changes for
  a person, and what stays as it was;
- **what you chose and why**, in one sentence;
- the address, in parentheses;
- an **empty slot for his correction**, with its allowed answers beside it in
  italics as in his block: *(empty — agreed · amend: how · replace: with what ·
  take it back)*.

No usefulness question here and no menu of fixes: he is not being asked, he is
being shown. **Silence is assent** — once he has returned the file, a row without
a correction stands. A correction either amends your decision or overturns it
(step 4). He may also take a row back: it is then written out in full in his
block, renumbered, and ruled on like the rest. The row is short on purpose; the
full finding, its check and the alternatives you weighed go into an appendix at
the end of the file, so the evidence is kept without being put in his way.

**The file is written in the owner's language.** The codes it coins (`N1`, `T4`)
are listed at its top with their meaning, one per line, and a term is explained
where it first appears — the same duty, one level down, as keeping the mechanism
in parentheses. Its "how to fill it in" carries the four ranks of usefulness with
their definitions, one line each: the hint beside a slot names the ranks, and
the top of the file says what they mean.

**The removed block goes at the top of the same file** — what your refutations
killed, one line each: the finding's title and what refuted it. He scans it in a
minute and pulls any row back; a pulled-back row is renumbered into the body as
a normal finding.

**Before writing the first fix, put three moves on the table for yourself: patch
the place · rebuild the contour · cut the feature.** Then propose whichever are
actually sensible here. They may all be patches; one may be an amputation; the
point is not to offer a ladder but to have considered the rungs. What he sees is
your judgement of this finding, not a menu of scales.

This is the flaw the step once had. Its only question was about the finding
itself, and none asked what the answer to it was — so a finding whose right
answer was "rebuild this" got accepted and quietly patched, and the owner was
never asked the question he would have said yes to. The same three moves apply to
your own block, where nobody asks you at all: a decision you take alone is the
one most likely to be the local patch.

Do not rank the fixes and do not say which you would pick: that is a verdict
wearing the clothes of a fact. If none of them is what he wants, he writes his
own in the slot, and that is a datum rather than a failure of the file.

Three things stay out of the file until step 4, for the same reason. They live in
a **separate sealed file** — never a section of the review file, however it is
headed. Seen once: a wave put its predictions under "do not read until the
reveal" in the very note it was about to hand over, and whether they had been
read before the rulings could not be established afterwards. A sibling file at
least cannot be scrolled into.

- **your predicted mark of usefulness** — he anchors on it, and then the number
  measures whether he agrees with what you showed him. That is the Goodhart the
  lens-blindness rule in §3 exists to prevent, one seat further down. Facts
  inform; verdicts anchor.
- **your predicted decision and choice of fix** — the same mechanism, one axis
  over.
- **which lens produced it** — the lenses carry reputations in the ledger, and a
  reputation is an anchor like any other.

The sealed file goes in the lab if one is configured
(`<lab>/waves/W<NN>_sealed.md`), otherwise beside the review file, so it lives
where the review file lives and never in a code repository (below); the review
file names its path and says it is sealed until the reveal.

**Never filter by your own confidence**, on either question. "Ask what to do only
where I can see a big move" re-introduces precisely the bias under measurement —
the one that never sees the big move in the first place.

**Where the review file lives:** the review note of §6, in the owning project's
folder of the owner's notes repository, beside the project's design notes, at
its final path. **Never in a code repository**, even when the object under
review lives in one and the run starts there: the reviews follow the design
notes, which the owner keeps in his notes repository, and a client's code
repository is no place for his rulings and predictions. A run started in a code
repository writes the review file and the sealed file into the notes repository
by the path its bridge to it names. The review file sits at that final path —
the same file the wave lands in, written now in its before-rulings form rather
than drafted somewhere and moved later. It opens with
its codes and how to fill it in, then what ran and under what limits, then the
removed block, then his block, then yours, then the appendix.

**Then one message in chat, and nothing more:** what ran and in what mode, how
many findings wait for his decision and how many you decided yourself, the counts
by severity and axis, the path to the file, the run's cost, and the two ways he
can answer. Nothing step 4 hides. Do not paste the findings into chat as well —
the file is the artifact, and a chat copy is what the per-finding dialog turns
back into.

**He answers however suits him:** comments or filled slots in the file, or a list
in chat by number. Accept both, in any mix, and never push him toward one form.
If his answers leave gaps — a finding in his block with no decision, an "into a
task" with no task, a usefulness slot left empty, a correction that contradicts a
requirement or another of his rulings — collect them all and ask them in **one**
message at the end. That is the only question you put to him per wave.

**A slot he leaves empty after that is recorded as empty.** Never fold a blank
into a mark: a wave whose blank answers were all read as acceptance carried the
main thread's judgement inside the owner's number, and the number was then quoted
as his. **Read every correction against the object before you classify it** — it
is his decision about your decision, and it may collide with something neither of
you had in view.

**Then wait.** No reminders, no re-summarising, no starting to land the obvious
ones — yours included: a row of your own block is landed only once he has
returned the file, because a correction may overturn it. If the session ends
before he rules, that is normal: resuming enters here,
at step 3, with the lenses not re-run, the checks not re-run, the predictions not
re-written, and the sealed file unopened — the resuming session stays as blind as
the owner.

**Step 4 — reveal, then record.** Once he has returned the file, open the sealed
file and write two tables **into the review file**, with the numbers of §6 under
them; in chat, the headline and the numbers, not the tables again.

- **His block:** finding · lens · predicted usefulness · his mark · agree? ·
  predicted decision · his decision · whose fix (yours · his own · handed to you).
- **Your block:** finding · lens · what you chose · his correction — none ·
  **amended** (your decision stands, made more exact or wider) · **overturned** (a
  different decision replaces yours) — and beside the table the three counts he
  reads it by: decisions accepted · amended · overturned, plus the rows he took
  back.

Name the disagreements plainly and do not argue them — a disagreement is a
labelled example, which is worth more than being right.

**If a chosen fix changes the shape of the object rather than repairing a place
in it, re-check the remaining findings — his and yours — against the new shape
before anything is landed.** A feature being cut takes its findings with it, and landing
repairs to something that will not exist is worse than wasted. Say which findings
the ruling voided. Nothing is landed before this point, so the order is already
safe.

**Backdated ratification** (a wave triaged before this section existed) runs the
same way: read the findings out of that wave's review note, write them into a
review file in the shape of step 3 — sorted, in the owner's terms, both
questions — and do not show the verdicts already written there. Its record then
names two versions that differ (§6): the charter those lenses ran under, and the
skill that is ratifying it now. **Enter the skill here** — §§1–4 already happened, so do not re-run
lenses; step 0b still applies, because the lab is where the result goes and it
names which wave is waiting.

**When the owner was never in the session at all,** nothing about the protocol
changes — the file is written the same way, because the file *is* the protocol
now. Close with the same chat message step 3 asks for, add the words that resume
the wave later, and leave it. The old "parked ratification" mode was the
difference between a file and a dialog; that difference is gone.

## 6. Land it

- **Review note** — the file step 3 already wrote, now completed rather than
  written again: his rulings and chosen fixes filled in where the answer slots
  were, the reveal table of step 4 appended, and the note wired into wherever the
  owning project lists its notes. What it holds by the end: what ran and under
  what limits · what verification removed · his block, `concept` before `detail`
  and by severity within each, each finding with his mark and the decision he
  took · your block, each row with his correction or none · findings waiting for
  the showing · findings moved into tasks · findings voided by a fix that changed
  the object's shape · inter-lens disagreement as a decision · what the run said
  about the Critic itself. Under manual ratification the **owner's answer is the
  verdict of record**; yours is kept beside it as the prediction, not quietly
  replaced by his.
- **Carry every deferred finding into its task.** With the owner's yes, add to
  the task he named a subtask whose title is the finding's one line and whose
  description carries the finding as he read it, the check, the candidate fixes
  with their costs, and a link to the review note — enough for the session that
  opens that task to act without this conversation. Record `deferred → <task>`
  in the ledger. A deferred finding keeps his mark of usefulness and stays out of
  the fix-hit-rate denominator: no fix was chosen.
- **Carry every finding that waits for the showing to where the showing
  happens.** "When I see it" is a promise that someone will show him. With his
  yes, add to the task that builds the thing a subtask that says what to put in
  front of him and which finding it answers; where there is no task to carry it,
  the review note's block of findings waiting for the showing is the record, and
  the closing chat message names it. The finding is open, not accepted: it stays
  out of the fix-hit-rate denominator, and out of the usefulness count unless he
  marked it anyway.
- **Land the fix he chose, at the size he chose it.** If that is a rebuild or a
  removal, it is a change to the design and it lands as one. Do not substitute
  the patch you had ready because it is the cheaper thing to write — that
  substitution is the failure the second question exists to catch, and making it
  after he has ruled is worse than never asking.
- **The wave record — write this first, because everything else reads it.** One
  YAML file at `<lab>/waves/W<NN>.yaml`, from the template at
  `${CLAUDE_PLUGIN_ROOT}/lab/wave_template.yaml`: the runs (one entry per run,
  with its lens, model, arm, **raw findings**, the **topic ids** it named, and
  `duration_ms` and `tool_uses` copied as they stand from the usage line of the
  agent's result, and `reads: batch` on a run launched with that line), and
  the findings after the merge (topic, the runs it came `from`, severity, axis,
  `status`, the `block` it was shown in, and once he has answered — for his
  block, your two predictions beside his mark, his decision and whose fix he
  took; for yours, `correction`: `accepted` for every row he left alone,
  `amended` or `overturned` for the rest). "Your choice" is `fix: delegated`,
  never `mine`; "when I see it" is `ruling: until_shown`; a row he took back
  moves to `block: owner` with `returned: true`. A finding you removed carries
  `status: removed` with the refutation that removed it; a finding of your own
  outside the lenses carries `from: []`. **Record two versions:**
  `charter_version` — the charter the lenses actually ran under, which is the
  snapshot taken when the session started — and `skill_version`, this text. They
  separate two different sets of numbers (step 0c), and they can differ inside
  one session.
  Then validate and compute, in that order:

  ```
  python "${CLAUDE_PLUGIN_ROOT}/tools/wave_stats.py" --lab <lab dir> check W<NN>
  python "${CLAUDE_PLUGIN_ROOT}/tools/wave_stats.py" --lab <lab dir> stats W<NN>
  ```

  `check` refuses a record that does not hold together — a topic attributed to a
  run that never named it, a removal with no refutation, a lens outside the three,
  an owner's mark on a row of your own block, the vocabulary of one skill era in a
  record of the other. Each of those, unvalidated, yields a plausible number
  rather than an error.
- **The lab** *(if there is one)*: lens ledger row **from the tool's output, not
  retyped from memory**, any new tic, any new hypothesis (never into the desk
  until a clean run confirms it), plus one **ratification row per finding** —
  his mark and his decision for a finding of his block, his correction for a row
  of yours.
- **The yield of the uncapped lenses, per lens.** Since the cap came off, the
  ledger row carries for each lens run: raw findings, topics after its own
  wording-duplicates were merged, and topics only it gave in this wave — all three
  printed by `stats`. Nothing is concluded from one wave: the accumulating median
  of "topics only this lens gave" (`wave_stats.py … median`) is what the owner
  rules the removed cap on, and a wave that skips its record removes itself from
  that median without saying so.
- **The hypotheses journal** *(in the lab)*: an `enhanced` run appends its
  stability numbers (topics per run, union, share found by every run of a
  lens, pairwise overlap, cost); an `experimental` run appends one measurement
  row to the hypothesis it served — the arms, the topic unions, the findings per
  arm that were not noise and how many of them changed a decision, the tokens per
  arm, and each arm's minutes when time is what the hypothesis is about. A
  hypothesis is confirmed or refuted
  by the owner on the journal, never by the main thread on one wave.
- **The desk** *(if the repository keeps its own)*: only techniques confirmed
  enough to teach. Never write to the bundled generic desk from a run — a plugin
  update overwrites it.
- **Land the outcomes** by whatever convention this repository uses for session
  outcomes.
- State the cost in tokens and **four** numbers, never one. With a lab
  configured these come from `wave_stats.py stats`, which knows each of the
  denominators below; without one, compute them by these definitions and say that
  you did it by hand:
  - **usefulness** = his marks over **the findings of his block that he rated**:
    the share that changed a decision is the headline, the shares that extended
    one and that were noise stand beside it, and the count he rated goes with
    them. This is the number about
    the *lenses*, and the one a version of the critic is compared by. Say the raw
    count beside it whenever your refutations removed anything — a share quoted
    alone hides how much you cut.
  - **triage agreement** = the share where your prediction matched him — once for
    the mark of usefulness, once for the decision. The measured size of the
    authorship confound, and a number about *you*, not about the lenses.
  - **fix hit rate** = the share where he took one of the fixes you offered
    rather than writing his own — a number about your repertoire. **"Your choice"
    is out of its denominator and counted beside it**: he chose nobody's fix.
    Counted as a hit it flatters the rate by exactly the findings he declined to
    rule on. Not fixing, a task and "when I see it" are out as well.
  - **your own decisions** = accepted · amended · overturned, over the rows of
    your block, with the rows he took back beside them.
  Read them together. A low agreement with a high usefulness means the lenses are
  fine and your triage is not. A low fix hit rate means the lenses find the right
  things and you keep reaching for the wrong instrument — usually the small one.
  Many "your choice" answers mean the line between the blocks is drawn too far
  toward him: findings reached him that were yours. Overturned and taken-back
  rows mean it is drawn too far toward you. Report the failures that way round;
  they are the more useful ones.
  **None of the four compares with a wave run under a skill before 0.9.0** —
  those asked whether a finding was true, and reported precision. **The shares
  of usefulness and the agreement on usefulness do not compare across 0.10.0
  either**: three ranks counted an addition as a changed decision, and the tool
  keeps the two scales in separate tables. The agreement on the decision, the fix
  hit rate and your own decisions cross that line. The lens-side yield does
  compare, as long as the charter and the launch have not moved (step 0c) — and
  0.10.0 moved the launch: the topic pass of a `normal` wave runs on Opus now,
  so a `normal` wave's lens-side numbers compare only with waves whose topic
  pass ran on the same model. The record says which (`topic_pass`), and
  `median` splits its series by it.

## 7. Two standing cautions

- **Agent definitions are snapshotted.** A charter edit does not reach a run that
  is already under way. If the charter changed this session, say so and treat the
  results as run against the previous version.
- **Effort is the owner's money.** `normal` unless he said otherwise; a third
  run, a second stage, a dearer model — each is offered with its cost and
  launched on his word. A wave that quietly ran at `enhanced` is a wave whose
  numbers cannot be compared with the ones before it.
- **Edit the source, never the installed copy.** The charter that runs is the
  installed one; editing it in place is silently undone by the next update, and
  editing the source repository does not reach the installed copy until
  `claude plugin update kai-critic` and a restart. Change the source, bump the
  version, update, and only then trust that a run is testing the new text.
