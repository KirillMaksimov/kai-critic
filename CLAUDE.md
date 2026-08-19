# kai-critic — repository instructions

Source of the `kai-critic` Claude Code plugin: an adversarial critic over a proposal
reality has not tested yet. Three components and nothing else — a charter
(`agents/kai-critic.md`), a run protocol (`skills/kai-critic/SKILL.md`), and a
generic desk (`desk/desk_critic.md`). No code, no dependencies, no MCP server.

## The two-file rule — the one thing not to break

**Desk** = what we teach the agent; read before every run.
**Lab** = what we measure it by — lens ledger, precision, tics, hypotheses under
test; read on **no** run, ever.

This repository ships a desk and deliberately ships **no** lab. Never move a
measurement into the desk, and never add a lab file here for convenience: an agent
that has read the hypothesis stops being its test, and a lens that has read its own
precision starts playing to the scoreboard. If a technique is confirmed enough to
teach, it moves desk-ward as craft — never as a score.

## Editing

- **Edit here, never the installed copy.** The charter that actually runs is the
  one under `~/.claude/plugins/cache/…`; editing it in place is undone by the next
  update. Change the source, bump `version` in `.claude-plugin/plugin.json`, then
  `claude plugin update kai-critic` and restart the host.
- **Agent definitions are snapshotted at launch.** A charter edit does not reach a
  run already under way. Any run started before an edit was applied was run against
  the previous text — say so rather than reporting it as a result about the new one.
- `claude plugin validate .` before committing a manifest change.

## Public-repo hygiene

Everything here is public. Keep it that way:

- **No names, no clients, no project paths.** The charter says *the owner* and must
  keep saying it — an earlier version asked whether something "fits his weekly
  capacity", which is the personalisation that made it unpublishable.
- **Examples are anonymised craft, not war stories.** "One run turned up three
  different sizes for the same artifact" teaches the technique; naming the artifact
  teaches nothing extra and leaks.
- **No calibration numbers.** Precision figures belong in a private lab, alongside
  the objects they were measured on.

## What lives elsewhere

The charter and the skill are written to work with **no** desk and **no** lab — a
repository that has neither still gets a full run. Anything host-specific reaches
the plugin two ways only: the `desk_path` user option, and whatever the host
repository's own instructions say about where its lab lives. Do not add a third.

## Abbreviations in design & research output

Any design or research deliverable — a note written in this repo **or** the same content sent to the user as a chat message — opens with a legend of its short codes, above the body, in the language of the text (`CODE — expansion`, one per line). Covers coined indices (`D1`, `W11`), domain acronyms (`FN`, `SP`) and anything not spelled out at its first use; leaves out the universally known (API, JSON, git). An edit that introduces a new code extends the legend in the same edit. Prefer a speaking name over a coined index — the legend is a fallback, not a licence. The same duty for terms rather than codes: a term, anglicism or coined name gets its expansion in parentheses at its first use, after which it may be used bare.
