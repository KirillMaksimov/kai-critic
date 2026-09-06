# kai-critic — repository instructions

Source of the `kai-critic` Claude Code plugin: an adversarial critic over a proposal
reality has not tested yet. What it ships:

| Path | What it is |
|---|---|
| `agents/kai-critic.md` | the charter — one lens per invocation |
| `agents/kai-topics.md` | the topic pass that runs first |
| `skills/kai-critic/SKILL.md` | the run protocol, executed by the main thread |
| `desk/desk_critic.md` | the generic desk, read before every run |
| `lab/` | the **empty shape** of a lab: template, wave-record schema, README |
| `tools/wave_stats.py` | the deterministic number layer, plus its guard |

Python 3.10+ and `pyyaml` for the tool; nothing else, and no MCP server. Everything
apart from `tools/` is plain markdown and runs with no dependencies at all.

## The two-file rule — the one thing not to break

**Desk** = what we teach the agent; read before every run.
**Lab** = what we measure it by — lens ledger, precision, tics, hypotheses under
test; read on **no** run, ever.

This repository ships a desk, and it ships the **shape** of a lab — a template with
no data in it — and never a lab's contents. Never move a measurement into the desk,
and never add a real lab file here for convenience: an agent that has read the
hypothesis stops being its test, and a lens that has read its own precision starts
playing to the scoreboard. If a technique is confirmed enough to teach, it moves
desk-ward as craft — never as a score.

**Shapes ship, data does not.** `lab/lab_template.md`, `lab/wave_template.yaml` and
`lab/README.md` are the only files `lab/` may contain. A real lab holds its owner's
objects, failures and rulings, so it lives in **their** repository — and it would be
destroyed here anyway, because a plugin update replaces this directory. `.gitignore`
enforces it: `lab/waves/` and every `lab/*.md` but the two templates are refused, so
a private record cannot be committed here by accident. If you add a file under
`lab/`, add its exception in the same edit or it will silently not ship.

## Editing

- **Edit here, never the installed copy.** The charter that actually runs is the
  one under `~/.claude/plugins/cache/…`; editing it in place is undone by the next
  update. Change the source, bump `version` in `.claude-plugin/plugin.json`, then
  `claude plugin update kai-critic` and restart the host.
- **A version bump and a `CHANGELOG.md` entry are one commit, never two.** The
  bump alone says a release happened and not what changed in it, which is worth
  little to a reader and nothing to the next run trying to work out which text a
  wave was run against.
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
the plugin through **user options only**: `desk_path` and `lab_path`. Do not add a
third mechanism, and in particular do not let the skill say "wherever this
repository keeps it" — that phrasing was here until 2026-09-06 and it is the shape
of the mistake below.

**A skill may only name machinery the plugin ships or a user option supplies.**
The number layer was first designed to live in the host repository, with the skill
pointing at it as "if the repository provides a tool". Kirill stopped it: a fresh
install would then have a run protocol talking about something that does not exist,
and the alternative phrasing is so vague it cannot be followed. So the tool ships
here and is invoked through `${CLAUDE_PLUGIN_ROOT}`, while the *data* it reads is
named by a user option. Every future extension splits the same way — **the
machinery is ours, the data is theirs** — and a skill sentence that cannot name a
path under `${CLAUDE_PLUGIN_ROOT}` or a `${user_config.*}` value is a sentence that
does not belong in the skill.

**A `userConfig` entry's `type` must be one the host actually supports.** `file` is
the verified one; `directory` was used here for a day and silently would not have
rendered its field. When a path could be either, take the file and derive the rest
from it — `tools/wave_stats.py` accepts the lab file or its directory for exactly
this reason. `claude plugin validate .` does not catch this: it checks the
marketplace manifest, not the option schema.

## Abbreviations in design & research output

Any design or research deliverable — a note written in this repo **or** the same content sent to the user as a chat message — opens with a legend of its short codes, above the body, in the language of the text (`CODE — expansion`, one per line). Covers coined indices (`D1`, `W11`), domain acronyms (`FN`, `SP`) and anything not spelled out at its first use; leaves out the universally known (API, JSON, git). An edit that introduces a new code extends the legend in the same edit. Prefer a speaking name over a coined index — the legend is a fallback, not a licence. The same duty for terms rather than codes: a term, anglicism or coined name gets its expansion in parentheses at its first use, after which it may be used bare.
