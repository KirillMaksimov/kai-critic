# Changelog

All notable changes to this plugin are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions are the
`version` field of `.claude-plugin/plugin.json`, and a release is a version bump
plus an entry here in the same commit.

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
