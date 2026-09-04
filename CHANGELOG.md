# Changelog

All notable changes to this plugin are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions are the
`version` field of `.claude-plugin/plugin.json`, and a release is a version bump
plus an entry here in the same commit.

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
