# Changelog

All notable changes to this plugin are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions are the
`version` field of `.claude-plugin/plugin.json`, and a release is a version bump
plus an entry here in the same commit.

## [0.13.0] — 2026-09-30

Two proposals of a retrospective over the first thirty-one waves, both picked by
the owner: the number layer stops making the main thread bend a record to fit
it, and the merge gains the job its strongest own findings have always come
from.

### Added

- **Merge job 5 — run it and look at what comes out** (skill §4). The lenses
  only read; what the object actually produces never reaches them. Wherever a
  lens took a behaviour on trust, the main thread runs the object's own tool,
  query or report against live data, read-only, and looks at the top of what
  it returns. The strongest findings the main thread ever added came from
  here — in about ten waves — and the lab had asked for it as a step since an
  early wave. A finding born here carries `from: []` and goes through
  verification like any other. Not a fourth lens, and nothing that writes,
  sends or spends. The README's merge paragraph now names all five jobs.
- **`extra_topics` on a run.** A lens finding that carried two topics used to
  be recorded by splitting the lens's raw count, so the record held a number
  the lens never returned (three waves had to). `raw_findings` now stays what
  the lens returned, and `extra_topics` says how many topics beyond one per
  finding its findings carried.
- **`median` splits by the text the lenses read.** `LENS_TEXT_CHANGES` lists the
  versions that changed the charter or the topic pass (0.5.0, 0.6.0, 0.9.2,
  0.10.2, 0.11.0, 0.12.0); a record's lens text is the latest of them at or
  below its `charter_version`. Skill step 0c always said lens-side numbers
  compare only under one text; the tool split by the cap alone. On an existing
  lab this moves waves run under 0.9.2 with a Sonnet topic pass into a series
  of their own, apart from those run under 0.6.0–0.8.0.
- **Set-asides counted apart from refutations.** A removal whose reason opens
  with `outside the delivery` (the owner's standing ruling, 0.12.0) is printed
  by `stats` on its own line and in a `ledger` column; the total removed is
  unchanged.
- **The main thread's half of the cost**: `main_thread.duration_ms` (launch of
  the topic pass to the review file on disk, from two timestamps) and
  `main_thread.tokens` (only when the host reports the session's usage). Until
  now only subagent tokens were recorded, although the skill asks which half
  grew.
- **`authored_in_session`** — whether the session that ran the wave also wrote
  the object, the authorship confound every agreement number has carried as a
  footnote. `stats` prints it, `ledger` shows it per wave.
- **`reach` is read.** `check` refuses a reach it cannot parse — "N of M …",
  «N из M …», whole object, or not counted — and a count larger than its
  whole. A new command, `reach`, groups the owner's marks by the reach they
  were shown with, in descriptive buckets that no rule reads as a threshold.
- The guard covers each of these; the template and `lab/README.md` document
  the new fields.

### Note

The merge job is a skill change inside §4, but it adds findings of the main
thread's own (`from: []`), which belong to no run: lens-side numbers are
untouched. The main thread's ratios count what it shows, so more findings may
reach the owner. The `median` split changes how existing numbers are grouped,
not the numbers.

## [0.12.0] — 2026-09-30

Two lessons from one wave, both the owner's. Four of the eleven findings he
ruled on came back as noise, and every one had been predicted useful: one
touched nine items of about thirteen hundred and was shown without that count;
the other three were about his plans, about a second delivery nobody has
decided, and about carrying settings over to a recipient who has not had a
first delivery. The topic pass listed all four; the lenses filed them.

### Added

- **A `Reach` line in every finding** (charter §4): how much of what the object
  acts on the finding touches, as a count against its whole and where the count
  came from — or `whole object`, or `not counted — <what would count it>`.
  **Severity follows reach**, and the charter says why with the case above.
- **Charter §3 rule 11 — judge the delivery in front of you.** Three kinds of
  finding are not findings on a design or an instruction: the owner's plans
  (his week, tasks, hours, dates — still asked on a `strategy`, where the plan
  is the object), a later delivery nobody has decided (an open fork about it in
  a neighbour included), and state that only the delivery under review would
  create. A lens writes them under `Checked and found sound` as `outside the
  delivery: <kind>`. The topic pass gets the same rule (its rule 8) and lists
  them under `Set aside`. B2 now says it asks about the cost of running the
  thing, not about whether building it fits the owner's schedule.
- **The main thread measures the reach** (skill §5 step 1): against the live
  data, read-only, wherever the session can reach it — the lens's line is where
  to start, not the answer. The count goes into the entry beside severity and
  axis in the owner's units with its share, and a severity it does not carry is
  lowered with the reason given. Usefulness is **predicted by the reach first**:
  a small share predicts noise unless the few cases are the ones the object
  exists for.
- **The three classes are handled by the owner's standing ruling**, the one
  narrow exception to "only a refutation removes a finding". A finding about
  his plans is never written into the review file — at most one line in the
  closing chat message. A later delivery or state not yet created goes into the
  removed block with its class as the reason, where he can pull it back. The
  record carries `removed_reason: "outside the delivery — <kind>"`, so these
  removals can be counted apart from refutations.
- **`reach` in the wave record**, optional, beside severity. `wave_stats.py` does
  not read it yet; it is kept so the ledger can later ask whether reach predicts
  the owner's mark. The template shows it and a set-aside finding.
- Both desks — this generic one and the owner's own — carry the two lessons as
  craft: count the reach before you rate, and the calendar and undelivered
  deliveries are not the critic's.

### Note

This is a charter change: the lenses and the topic pass read the new rule and
the new line. By step 0c the lens-side numbers after it do not compare with
the waves before it — fewer raw findings are expected, and that expectation is
the point, not a measurement. `wave_stats.py median` splits by the removal of
the cap, not by every charter version, so the owner's lab records the
boundary. The skill's side moves as well: removals now include standing-ruling
set-asides, told apart by their reason.

## [0.11.2] — 2026-09-30

### Changed

- **The scratch folder sits in the main checkout, never in a worktree.** 0.11.1
  put it at the root of the repository the session runs in, which for a
  worktree session is the worktree's own folder — deleted with the session, and
  the git-ignored scratch with it, which is the temp-folder problem again. The
  root is now the first `worktree` line of `git worktree list --porcelain`,
  which is the repository root itself when the session is not in a worktree.
  The `.kai/README.md` line lands there too, outside the session's branch: it is
  left uncommitted and named in the run's closing message.

## [0.11.1] — 2026-09-29

Where a run's scratch lives. §2 said "copy it to a scratch directory" and named
none, so one run put its snapshot, its lens prompt, its worksheet and its check
scripts in the machine's temp folder — which a cleanup empties, while the
snapshot has to stay readable until reality delivers the verdict.

### Changed

- **The scratch folder is `.kai/.critic/W<NN>/`** at the root of the repository
  the session runs in (a vault run: the vault root), beside the working folders
  the other kai plugins keep in `.kai/`. Every scratch file of the run goes
  there: the input snapshot, the common lens prompt, `topics.txt`, the
  worksheet and the throwaway check scripts. The review file and the sealed file
  keep their places from §5 step 3. Without a lab, the wave number is one past
  the highest folder already there.
- **The first write lays `.kai/.critic/.gitignore`** holding `*`, so the scratch
  is never committed and the repository's own `.gitignore` is left alone, and
  adds this plugin's line to the shared `.kai/README.md` by the convention the
  other kai plugins follow: the shared header when the file is absent, the line
  appended when it is missing, another plugin's line never touched.
- **Two guards the persistence calls for.** No lens is pointed at the folder as a
  whole, at a worksheet, or into another wave's folder — an old worksheet is a
  summary of previous runs. And nothing under `.kai/` is ever an instructions
  file, because the blind rule of §2 decides by what attaches to a named path.
- README says what a run leaves in the repository; CLAUDE.md records that the
  folder name is known to kai-readable-prose, whose judge excludes it.

### Note

The edit sits in §§2–3, but it moves only where the files live: a lens receives
the same content, and `topics.txt` reaches it by a different path. Lens numbers
are expected to compare across this version. That is an expectation, not a
measurement.

## [0.11.0] — 2026-09-29

The machinery for one experiment the owner agreed to: does grouping a lens's
reads into fewer turns make it faster without making it shallower? Each turn of
a lens costs a fixed few seconds before any thinking starts, and on one run more
than half of the bottleneck lens's turns issued a single read. Grouping could
also change how the lens follows a thread, which is why it is tested as an arm
and not landed.

### Added

- **`READS: batch`, a fourth optional task line in the charter.** Present, it
  asks the lens to issue the reads it already knows it needs in one turn; the
  charter says in the same place that nothing else changes — what it looks for,
  how far it follows a thread, when it stops. Absent, the lens runs as before.
  The skill lists it among the single factors an `experimental` wave may vary,
  with both arms fed from one topic pass so the list is not a second factor.
- **Time per run in the wave record**: `duration_ms` and `tool_uses`, copied as
  they stand from the usage line of the agent's result. Both optional. `stats`
  prints a run's minutes and calls, and per arm the slowest run — an arm's
  lenses run in parallel, so its time is a maximum, not a sum — and the calls
  summed. One unrecorded run blanks its arm's time rather than shrinking it.
  `check` refuses a negative or non-integer value.
- **`reads: batch` on a run, and a `median` split by it.** The median divided a
  wave into arms only when their topic passes ran on different models, so the
  batched arm of this A/B — which shares its topic pass with the plain arm by
  design — would have been pooled into the plain series without a word. Now a
  run's reading mode is a series key beside the topic pass's model; on the
  existing records every series and every value is unchanged.

### Note

The new paragraph is read by every lens, set or not. By step 0c that is a
charter change, and so was 0.10.2; the owner's lab records the boundary.

## [0.10.2] — 2026-09-29

A faster launch. The lenses start only when the message that launches them is
complete, and on one run the main thread spent about two minutes of that
message retyping the same forty-topic list into three prompts.

### Changed

- **The merged topic list is written once, to `topics.txt` in the run's scratch
  directory, and every lens gets `TOPICS: <path>`** instead of the list inline.
  In `MODE: blind` the list stays inline, as the desk does, so the
  single-artifact rule holds. The charter tells a lens to read the file in full
  on its first turn, before it reasons about the proposal, so the list reaches
  it where an inlined one would have. Its content, order and seat tags are
  unchanged — only the channel is — so lens numbers are expected to compare
  across this version. That is an expectation, not a measurement.

## [0.10.1] — 2026-09-28

The number layer catches up with the launch change of 0.10.0: the lenses read the
topic pass's list, so a median that pooled waves across two topic-pass models
mixed two configurations into one series.

### Fixed

- **`median` splits by the model of the topic pass as well as by charter era.**
  The model comes from `topic_pass` in the wave record; on an experimental wave
  whose arms ran topic passes on different models, a run takes its arm's model,
  each arm becomes a point of its own series (printed `W<NN>/A`) and uniqueness
  is measured inside the arm. A record without `topic_pass` is its own series,
  printed as unrecorded, never guessed into a model. Each point now carries the
  wave it came from.

### Added

- `check` refuses a per-arm `topic_pass` that leaves out a run's arm, and an
  entry that names no model: either would move runs into the unrecorded series
  without a word. An arm that ran without a topic pass says `runs: 0` and forms
  a series of its own.

## [0.10.0] — 2026-09-28

Three lessons from one wave, all ratified by the owner. Two change what the owner
is asked, so the main thread's usefulness numbers after this version do not
compare with the ones before it; one changes the launch of a `normal` run, so its
lens-side numbers compare only with waves whose topic pass ran on the same model.

### Changed

- **The topic pass runs on Opus at `normal` too**, not only at `enhanced`. An
  A/B on one object — one Opus topic pass against one Sonnet, the same Sonnet
  lenses behind each — gave the Opus arm a list twice as long and lenses that
  found several times more from it, for barely more tokens. The owner took the
  hypothesis as confirmed and made Opus the topic pass of every level.
- **Usefulness has four ranks, in the owner's own definitions**: changed a
  decision (a decision the design had taken is different) · **extended one**
  (the design stands, but a feature is added or what a person observes reaches
  further) · refined one (a small precision that changes nothing a person
  observes) · noise (unimportant, does not affect the delivery). Under three
  ranks an addition had nowhere to go and was counted as a changed decision.
- **Every empty answer slot in the review file carries its allowed answers
  beside it, in parentheses and in italics**, and the top of the file defines
  the four ranks. With bare slots the owner, who does not keep the scale in his
  head between waves, rated in his own words, and the main thread's mapping of
  those words onto the scale ended up inside his number.

### Added

- `wave_stats.py`: `extended` in the usefulness vocabulary, the share of
  extended findings beside the changed and the noise shares, and a `ledger`
  that prints three-rank and four-rank waves as two tables. A record rated on
  four ranks under an older skill says so with `useful_scale: 4`; `extended` in a
  three-rank record is refused.
- The wave template documents `topic_pass` (model, runs, topics), which records
  already carried: it is what says which lens-side numbers compare.

## [0.9.3] — 2026-09-26

Where the files of a run live. The owner keeps every design note, and so every
review, in his notes repository; a run over a design whose object lives in a
client's code repository must not leave its review or its sealed predictions
there.

### Changed

- **The review file and the sealed file never go into a code repository**, even
  when the object under review lives in one and the run starts there: both are
  written into the owning project's folder of the owner's notes repository,
  beside its design notes, by the path the session's bridge to it names. The
  sealed file still goes into the lab when one is configured, and otherwise
  beside the review file, which now always means the notes repository.

## [0.9.2] — 2026-09-25

Charter only. Its opening line still carried the stance of the capped-findings
era — "precision, not volume", "ten plausible observations are worse than three
real ones" — while rule 8 (since 0.6.0) moves deduplication and the discarding of
refuted findings to the main thread and calls a finding cut in advance work thrown
away. Sonnet follows such a stance literally and silently drops findings below
its own bar. Numbers from runs after this version compare with 0.9.1 with that
in mind: the lens was told to hold back, and no longer is.

### Fixed

- **The opening line asks for every finding that clears §3, with its
  confidence**, and says why: the main thread deduplicates and verifies, so a
  real finding held back is lost, and one the lens would not defend spends the
  owner's time.
- **Rule 8 loses its closing comparison** ("padding costs the reader more than
  an omission would"), which contradicted its own first half. The concrete bar
  stays: a finding you would not defend, one whose body says nothing breaks, or
  a restatement belongs in `## Checked and found sound` or nowhere.

## [0.9.1] — 2026-09-21

Docs only. The README still described a calling threshold that 0.8.0 removed
from the skill, so it contradicted §1 and its own "runs only when you ask"
paragraph further down. No skill, charter or tool text changed: every number
compares with 0.9.0 as it stood.

### Fixed

- **The protocol flowchart no longer opens with "Threshold met?"** and a branch
  that refuses to run. It opens with the owner asking, as §1 of the skill does.
- **The "Threshold" paragraph is replaced by who starts a run**: the owner, and
  nothing else; the cost of a run stated so he can decide with it in front of
  him; the one line the skill may say once about an object that looks small,
  after which it runs anyway.
- **The Layout section lists everything that ships.** `lab/` (the template, the
  wave-record schema, its README) and `tools/` (the number layer and its guard)
  have shipped since 0.7.0 and were missing; the manifest line named `desk_path`
  alone while `lab_path` has existed as long. The lab paragraph now says what the
  plugin does ship — the empty shape and the arithmetic — next to what it
  deliberately does not.

## [0.9.0] — 2026-09-21

The review file is rewritten for the person who actually reads it: an owner who
decides what the system does for a person and does not open the code. One wave
showed all four ways the old form failed him — a coined name read as an ordinary
word, so a verified finding was doubted; a finding that could only be judged by
looking at the built thing, with no ruling to say so; a finding written through
the internal names of a script's steps, understood not at all; and a finding that
was true while its meaning for a person was a different one. The lenses and the
charter are untouched: the language of a finding is born where the main thread
translates it, and that is where the change is.

**This release cuts the main thread's numbers off from every wave before it.**
Precision, triage agreement and fix hit rate as measured under a skill before
0.9.0 answered a different question and do not compare with anything after. The
charter did not move, so **the lens-side numbers — raw findings, topics, unique
topics, and the cross-wave median of unique topics per lens — run on through the
boundary unbroken.** Say so in the ledger row of the first wave after it, and in
every journal entry that quotes a baseline from before.

### Changed

- **Findings are sorted by who decides (§5, step 2).** *Requirement level* — what
  a person observes and gets: behaviour on the screens, the facts shown and their
  freshness, disk, load, his own time. *Specification level* — how the system is
  built so the requirement holds: queues, locks, tables, the order of steps in a
  script. A finding goes to the owner's block when ruling on it means choosing
  what a person will see or get; to the main thread's block when every sensible
  fix gives the person the same thing. The working test is to write the scenario
  first: if the options cannot be told apart by what a person sees, the choice is
  the main thread's; if unsure, it is the owner's, still in his terms. Sorting is
  not a filter — both blocks are in the file, and any row of the main thread's is
  the owner's to correct or take back.
- **A finding opens with scenario and effect.** Who does what → what they see or
  get that is wrong → what it threatens; a sequence is written as steps with
  actors. Internal names appear only as an address in parentheses after a phrase
  that already said it plainly — strike every parenthesis and the entry must still
  read whole. A coined name that is also an ordinary word is described, not named.
  Fixes are written as what changes for the person and what it costs.
- **The first question is "was it useful?", not "is it true?"** — three steps: it
  changed a decision · it refined one · noise. Truth stays with the main thread's
  verification and is stated in the file as a fact with its trace. An owner who
  does not read the code answers "is it true" with "you checked, so yes"; the
  ratio built on that saturated and measured the checker.
- **Two new answers to "what do we do".** *When I see it* — the finding cannot be
  judged on paper; it is not accepted, not rejected and not downgraded, it stays
  open, and §6 carries it to the task where the showing will happen. *Your
  choice* — the owner hands the decision back; recorded as `fix: delegated`,
  which is out of the fix-hit denominator instead of scoring as a hit.
- **The main thread's block is measured directly**: one row per finding — effect
  for a person, what was chosen and why, a slot for the owner's correction.
  Silence is assent; a correction is an amendment or an overturn; the count is
  decisions accepted · amended · overturned. No predictions are made for it.
- **Four numbers instead of three (§6)**: usefulness (share that changed a
  decision, share of noise, count rated) · triage agreement, once for the mark
  and once for the decision · fix hit rate without the delegated · the main
  thread's decisions. A blank answer is recorded as blank and never folded into a
  mark.
- **Step 0c says which numbers each kind of change cuts**: a charter change the
  lens-side ones, a skill change the main thread's ratios — and nothing lens-side
  as long as framing, launch and merge are left alone.

### Added

- **`skill_version` in the wave record — a second era axis.** `charter_version`
  alone could not express this release: the plugin has one version, but the
  charter is snapshotted when a session starts and the skill is read when it is
  invoked, so they can differ inside one session, and they separate different
  numbers. Required from 0.9.0; a record without it is read as the era before.
- **`wave_stats.py` computes each record by the rules of its own skill era.**
  `stats` names both versions in its header; `ledger` prints one table per era
  with the boundary stated between them, never one column through both; `median`
  stays split by charter only and says why a skill change does not cut it. The
  tool aggregates no main-thread ratio across waves in either era.
- **New record fields**: `block` (`owner` / `agent`), `useful` and
  `predicted_useful`, `correction`, `returned`; `ruling` takes `fix` · `no_fix` ·
  `into_task` · `until_shown`; `fix` takes `delegated`. `check` refuses a record
  that mixes the two eras' vocabularies, an owner's mark on a main-thread row, a
  repair on a decision that chose none — each of which would print a plausible
  ratio.
- The guard covers the new era, the untouched old one, and the shipped
  `wave_template.yaml` itself, which must pass `check`.

### Compatibility

Records written before 0.9.0 stay valid as they are and are computed as they
were. Do not convert them: a precision re-expressed as a usefulness share is a
number nobody measured.

### Depends on

The line between the two blocks uses a working glossary — *requirement* for what
a person observes and gets, *specification* for how the system is built so the
requirement holds — that was a draft when this release was written. If the
ratified wording differs, the names of the blocks and the list of what counts as
requirement level follow it; the mechanics do not change.

## [0.8.0] — 2026-09-12

Two owner decisions, both narrowing what the skill may do on its own.

### Changed

- **The run starts only when the owner asks.** §1 was a calling threshold — three
  conditions, any one of which licensed a session to launch the critic over work
  it had just produced, before showing that work. It is now a statement of who
  starts a run: the owner, by name, and nothing else. The cost of a run is stated
  so he can decide with it in front of him, and the skill may say once that an
  object looks small — then run anyway if he still wants the run. The old
  threshold also lived in the caller's own instructions (a vault `CLAUDE.md`
  convention, a design skill's landing step); those callers drop it in the same
  change.
- **Ratification happens in a file, never as a per-finding interview.** Step 3
  used to open one dialog per `concept` finding and two per `detail` finding;
  on a twenty-finding wave that spent the owner's evening on the dialog rather
  than on the findings. Now everything that survives verification is written into
  the review note in its before-rulings form — numbered findings, the removed
  block at the top, each entry carrying the check, lettered candidate fixes and
  two empty answer slots — and he answers in the file or by a list in chat, in
  any mix, at his own pace. The session writes it, says one thing in chat, and
  waits; gaps in his answers are collected and asked **once**, at the end. Two
  waves had already been ratified this way at his request (W18, W20).
- **The sealed-predictions file is now part of the default path**, not of a
  parked-wave mode: predictions are written **before the review file exists on
  disk**, because on W14 he began answering the moment the note appeared and a
  finding had to be dropped from the measurement. The separate-file rule stands
  for the reason it was found — a "do not read until the reveal" section inside
  the note being handed over cannot be shown to have gone unread.
- **"Parked ratification" is gone as a mode.** It was the difference between a
  file and a dialog, and the file is now the protocol; a wave run without the
  owner present differs only in that nobody answers yet. Resuming still enters at
  step 3 with lenses, checks and predictions untouched and the sealed file
  unopened.
- Step 4 writes its reveal table into the review file, with the headline and the
  three numbers in chat; §6 completes that same file rather than writing a note
  from scratch.

## [0.7.0] — 2026-09-06

The lab gets a deterministic layer. Every number the protocol asks for used to be
computed by the main thread in prose and retyped into a markdown table; now the
agent supplies one structured record per wave and a script computes the rest.
It found an arithmetic error on its first run.

### Added

- **`tools/wave_stats.py`** — the arithmetic: the four counts, the three ratios
  with their separate denominators, per-run and per-lens yield, topic overlaps
  and cores, per-arm cost, and the cross-wave median of unique topics per lens.
  `check` validates a record before anything is computed from it, because every
  integrity error it catches — a topic attributed to a run that never named it, a
  removal with no refutation, a lens outside the three — produces a plausible
  number rather than an exception.
- **`tools/test_wave_stats.py`** — plain-python guard, no framework. Each test
  protects a number a human would read as a fact and act on.
- **`lab/lab_template.md`, `lab/wave_template.yaml`, `lab/README.md`** — the empty
  shape of a lab and the record schema.
- **`lab_path` user config** — the directory holding your own lab and its
  `waves/`. The skill resolves it at step 0b, keeps it out of every run's allowed
  paths, and passes it to the tool.

**Your lab is yours and stays in your repository.** This plugin ships the empty
template and nothing else: a lab holds your objects, your failures and your
owner's rulings, and a plugin update replaces its own directory, so a record kept
here would be both exposed and destroyed. `.gitignore` refuses any real lab file
that lands in this tree.

### Changed

- **Step 0b names the tool** instead of gesturing at "whatever the repository
  provides". A skill that references machinery the installer does not have is
  either vague or wrong, and this one was heading for both.
- **§6 writes the wave record first**, then validates it, then reads its numbers
  off the tool. The ledger row is no longer retyped from memory.
- **The three ratios** are defined once, in the tool, and the skill points at it;
  without a lab they are computed by the stated definitions and the run says so.

### Found by the new layer, on the wave that motivated it

Backfilling the previous wave from its ratification registry reproduced precision
(31/31), triage agreement (15/30) and fix hit rate (31/31) exactly — and
disagreed on one per-arm count: 19 accepted findings for the second arm where the
hand tally said 18. The layer's split closes at 31 findings; the hand tally's
closes at 30. The consequence is small and real: the expensive topic model is
1.27× more cost-effective, not 1.34×.

The deeper cause was not arithmetic. **Nothing said how a merged finding should
be credited between arms**, so both numbers were defensible under rules nobody
had written. The rule is now stated — a finding counts for an arm when at least
one of that arm's runs produced it — which is the thing prose is not obliged to
do and a script cannot avoid.

## [0.6.1] — 2026-09-06

Fallout from lifting the cap, caught the same day: step 0c knew exactly one way
to test a hypothesis, and the hypothesis it had just been handed could not be
tested that way.

### Changed

- **Step 0c distinguishes the two shapes of hypothesis.** A configuration
  hypothesis — which model, how many runs, whether a stage is present — is an
  A/B on one object and belongs in `EFFORT: experimental`. A hypothesis about
  the charter or this skill is not: the text also decides how much work the main
  thread does downstream, so two arms would differ by more than the factor and
  nothing could be attributed. Those are settled by landing the change and
  watching the ledger accumulate. Offer the shape that fits, and say which it is.
- **A charter or skill change invalidates comparison with every wave before it.**
  New numbers may be read against waves under the same text and against the other
  arm of their own run, never against an earlier baseline. Journals quote
  baselines by name, and a later session has no way to see that the text moved —
  so the ledger row and the journal entry that owns the baseline both say it.

## [0.6.0] — 2026-09-06

The cap of seven findings per lens is gone. On the wave before this one it bound
all six lenses — every one of them returned exactly seven — so what a lens found
beyond the seventh was never observed, and the cut was made by a counter inside
an agent that had already paid to read everything. The cut moves to the main
thread, which has the paths, the tools and the owner.

### Changed

- **Charter rule 8: no cap on the number of findings.** A lens reports
  everything that clears its bar, ordered by severity. Deduplication and the
  discarding of refuted findings happen downstream. The bar itself does not
  move: a finding the lens would not defend, or a second wording of one it
  already gave, still belongs in `## Checked and found sound` or nowhere, and
  the charter says plainly that length is not a measure of a run.
- **The bundled desk** carries the same rule, so it cannot contradict the
  charter it is read alongside.
- **Skill §4 gained the fourth job it already had, and a warning about volume.**
  Duplicates are now merged *within* one lens as well as across seats — an
  uncapped lens restates itself, and that is not the two-seat agreement that
  raises severity.
- **Skill §5 step 1 now governs the discard.** Only a refutation that was
  actually run removes a finding; low confidence, small size and "he will reject
  it" do not, because those are rulings and the owner makes them. Everything
  removed goes to him as one scannable block, one line per finding with what
  refuted it, before the dialogs start, and any row he pulls back enters the
  triage as a normal finding. Verification runs in severity order, and a finding
  too expensive to settle is labelled unverified rather than chased or dropped.
- **Precision's denominator is now stated as the findings the owner saw**, with
  the raw count beside it whenever anything was removed — the two numbers stopped
  being the same one.
- **The ledger row records the yield per lens**: raw findings, topics after
  intra-lens merge, and topics only that lens gave. The accumulating median of
  the last one is what the removed cap will be judged on.

## [0.5.1] — 2026-09-04

The owner's call on the same day: the topic pass is not an experiment to
switch on, it is the first stage of every run.

### Changed

- **The topic pass runs by default** in `normal` (on Sonnet) and `enhanced`
  (on Opus); `agents/kai-topics.md` now defaults to Sonnet and `enhanced`
  lifts it through the `Agent` tool's `model` parameter. Whether the pass pays
  is still a question — the journal answers it with an experimental arm that
  runs *without* it, never by switching it off quietly. The run record names
  the pass's model and call count, so a wave with the pass is never compared
  blind with one that ran before it existed.
- The cost line for `normal` is about a million subagent tokens on a grounded
  design of ordinary size, up from three quarters.

## [0.5.0] — 2026-09-04

All of it came out of one measured wave: three identical runs of each lens on
one grounded design. A single run covered about half of what three runs found,
the adversary's runs shared no topic at all, and seven findings out of twenty
were accepted into work the owner had already planned rather than into the
object. The release answers those three facts.

### Added

- **A sweep in the charter.** Every lens answers a short list of *ways to look*
  before its free findings — three questions every seat asks in `grounded`
  mode (every named thing opened and checked; the neighbour's promise "when X
  exists this is handled there"; numbers checked against the artifact, not the
  document quoting it) and four per seat (the one real entry walked end to end;
  whose hours a system-term cost is; what the old mechanism did on the side;
  the level a promised control is implemented at; both ends of a retention
  rule; same problem twice, same answer once; the predecessor's fork; one-shot
  or standing sync; the rollback never mentioned). Each is answered explicitly
  in a new `## Sweep` section — found, nothing here, not applicable — so
  "nothing here" is a result and a skipped question is not. The sweep does not
  lower the bar: what it turns up still has to meet every rule.
- **Three optional task lines.** `SHAPE:` — one sentence on how the object
  changes the shape of what it replaces, a property of the object and not a
  hint; `TOPICS:` — the merged list of a topic pass, each entry dispositioned
  in a new `## Topics` section; `SWEEP: skip <ids>` — for experiments that
  switch a sweep question off.
- **A topic pass** (`agents/kai-topics.md`, Opus by default): stage one of a
  two-stage run. Reads the proposal from all three seats at once and returns up
  to forty candidate topics — a question and a check phrase each, tagged by
  seat, no severity, no verification, no solutions. The lenses then take the
  list as a floor under their coverage and still run their own sweep. Until the
  owner's journal says the pass pays, it is an experimental configuration.
- **Effort levels** in the run protocol, the owner's choice and never escalated
  by the main thread: `normal` (one run per lens, Sonnet), `enhanced` (two runs
  per lens in one batch, a third offered per lens only while its second run
  still added topics), `experimental` (an A/B on one object, two configurations
  differing in exactly one factor, serving a hypothesis from the lab).
- **Topics as the unit of measurement.** Merge job 4 maps every finding to a
  topic — the same problem found in different words by different runs — and
  keeps the run × topic matrix. Saturation, the third-run offer, the stability
  numbers for the ledger and the comparison between experimental arms are all
  read from it. A divergence picture shown before ratification carries run
  numbers and hides the lenses.
- **Step 0c — the hypotheses journal.** If the lab keeps a journal of what is
  believed about the mechanism itself (which model, how many runs, whether the
  topic pass pays), the main thread reads it before a run and may *offer* the
  owner to serve one hypothesis with this run. The lenses never learn a
  hypothesis exists.
- **A ruling of its own: "into a task".** The second ratification question
  gains an option for a finding that is true, accepted, and belongs to work the
  owner has planned rather than to this object. The main thread then asks which
  task, and — with his yes — carries the finding there as a subtask whose
  description is enough for a session that has never seen this conversation.
  Counted as accepted for precision, outside the fix-hit-rate denominator. The
  triage rule that goes with it: a finding about a channel outside the object —
  diagnostics, backup, delivery, monitoring, security — is predicted as
  deferred, not as a plain acceptance; measured three waves running as the most
  repeatable miss.
- **Hard rule 10:** paths outside the list are outside the run; one opened
  anyway is named in the header as a breach, and a finding resting on it is a
  check to run. The header also carries the shape the lens took.

### Changed

- Landing appends stability numbers (enhanced) or one measurement row
  (experimental) to the hypotheses journal; a hypothesis is confirmed or
  refuted by the owner on the journal, never by the main thread on one wave.
- A third standing caution: effort is the owner's money.

## [0.4.0] — 2026-08-27

Recorded retroactively in the 0.5.0 release: the bump shipped without its
entry, which is exactly the omission the rule at the top of this file exists
to prevent.

### Changed

- **Before predicting a plain "accepted", the main thread asks whether the
  finding opens a decision or closes one.** A finding with one obvious repair
  closes its topic and is usually accepted as written; a finding that exposes a
  fork — where a thing should live, who owns it, which of two contours it
  belongs to — is accepted *with a correction*, because the owner supplies the
  choice the lens could not. Predicting a plain acceptance on a fork-shaped
  finding was the single most repeatable triage error measured.

## [0.3.0] — 2026-08-25

Both changes came out of ratifying one live wave: the first from the owner's own
words during it, the second from how that wave had to improvise a stop.

### Added

- **Every finding carries an axis: `detail` | `concept`.** `detail` — the
  proposal under-specifies a step, and spelling it out settles the matter.
  `concept` — the problem sits in the design itself — a contradiction, a cost, a
  source of noise that survives any amount of specification — and needs the
  owner's judgement. The lens marks it (tie-break: would a fully-specified
  version still have the problem?), the merge keeps it (`concept` wins a lens
  disagreement; chains and promoted tails get theirs from the main thread), and
  ratification is ordered by it: `concept` first, one per dialog with the full
  treatment; `detail` after, two to a dialog, fixes ready to land as written.
  Severity says how much a finding matters; the axis says how it should be read
  — where the owner must think, and what he can wave through in minutes. The
  axis is shown at ratification: it is the lens's claim about where the problem
  lives, the same kind of fact as severity, so it does not join the hidden trio.
- **Parked ratification.** A wave run in a session the owner is not in had no
  protocol for stopping before the dialogs. Seen in the wild: predictions parked
  in a section of the very note the owner would ratify from, below a header
  saying "do not read until the reveal" — and whether they were read could not
  be measured afterwards. §5 now says how to park: the note draft carries what
  step 3 shows (findings with axes, checks, candidate fixes) and none of what
  step 4 reveals; predictions and lens names go to a separate file the note
  names — the lab if the repository keeps one, else a sibling file — sealed
  until the reveal; the session closes with a parking notice in chat and the
  words that resume it. Resuming enters §5 at step 3: nothing is re-run or
  re-predicted, and the parking file is opened only at the reveal, which keeps
  the presenting session as blind as the owner.

## [0.2.0] — 2026-08-24

Two protocol changes to ratification, and one to how a run is framed. All three
came out of live waves, and two of them pull against each other — the second
change is written the way it is because the naive form of the first would have
made the third worse.

### Added

- **Ratification asks two questions per finding, not one.** The four options —
  accept, accept with correction, downgrade, reject — all asked whether the
  finding was *true*, and none asked what the answer to it was. A valid finding
  whose right answer was "rebuild this" or "cut this" had nowhere to go: it was
  accepted, and a local patch was landed. The dialog now carries a second
  question, *what do we do*, whose options are the fixes the main thread judges
  sensible, plus "don't fix", plus the owner's own in free text.
- **The main thread must consider three moves before proposing any fix** — patch
  the place, rebuild the contour, cut the feature — and then propose whichever
  are actually sensible for that finding. Not a ladder of scales: the moves are a
  discipline for the author of the fixes, not a menu for the owner.
- **`fix hit rate`**, a third number beside precision and triage agreement: the
  share of findings where the owner took an offered fix rather than writing his
  own. It measures the main thread's repertoire, and specifically the standing
  bias it exists to catch — an agent proposes the repair it can write, which is
  almost always the local one. Rejected findings are out of its denominator.
- **A verified finding about behaviour now reaches the owner as a reproduction** —
  the input, the call, what came out and what should have — instead of a summary
  of the check. Findings about *absence* keep the fact as it stands; a trace
  invented for them would be manufactured evidence.
- **Hard rule 9 in the charter**: standing instruction files the host attaches on
  its own (a directory's `CLAUDE.md` or equivalent) are environment. The lens
  reads them — when the object under review is a repository's own machinery, its
  instructions are part of what is being judged — does not obey them, does not
  treat them as part of the proposal, and names them in its `## Run` header under
  a new `Files received but not listed` line.

### Changed

- **`grounded` framing enumerates what the host will attach** and lists it with
  the readable paths. The problem was never that a lens read those files; it was
  a record saying ten paths when the lens read twelve, which cannot be reproduced
  or deliberately repeated.
- **`blind` framing no longer allows a named path with anything standing above
  it.** The measurement behind the single-path form (cheaper by 3×, equally
  blind) was taken on artifacts with nothing above them and does not carry into
  an instrumented repository. Inline the artifact instead.
- **A chosen fix that changes the object's shape is retroactive over the wave.**
  Before anything is landed, the remaining accepted findings are re-checked
  against the new shape, and the ones the ruling voided are named. Nothing lands
  before every finding is ruled, so the order was already safe; it is now said.
- Landing follows the fix the owner chose, at the size he chose it. Substituting
  the cheaper patch after he has ruled is worse than never having asked.
- The main thread now writes down **two** predictions before the first dialog —
  the ruling and the choice of fix — and both stay hidden until the reveal, along
  with the lens name.

## [0.1.0] — 2026-08-11

Initial import: the plugin extracted from the private vault it grew up in, with
every reference to its owner's projects, paths and conventions removed.

- **Charter** (`agents/kai-critic.md`) — one lens per invocation
  (beneficiary / adversary / auditor), `Read`/`Grep`/`Glob` only, no `Agent`
  tool, at most seven findings, names problems and never writes solutions.
- **Run protocol** (`skills/kai-critic/SKILL.md`) — calling threshold, framing by
  whether reality exists yet, three lenses launched in one parallel blind batch,
  merge as three jobs, blind ratification by the owner, landing.
- **Generic desk** (`desk/desk_critic.md`), overridable through the `desk_path`
  user option, and deliberately **no** lab: an agent that has read the hypothesis
  stops being its test.
