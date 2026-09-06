# The lab — optional infrastructure, and yours

The Critic runs perfectly well without a lab. What a lab buys is the answer to
"is this working": the ledger of what each lens has produced, the calibration
history, the hypotheses about the mechanism, and the numbers that settle them.

**The plugin ships the empty shape; your lab is yours and lives in your own
repository.** Two reasons, and the second is the hard one:

1. A plugin update replaces the plugin's directory. Records kept here are
   destroyed by the next install.
2. A lab holds your objects, your failures and your owner's rulings. That is
   private material, and it must never end up in a public plugin repository.

This directory therefore contains a template and nothing else, and the plugin's
`.gitignore` refuses any `waves/` directory so a private record cannot be
committed here by accident.

## Setting one up

1. Copy `lab_template.md` into your repository — anywhere, next to the work it
   measures. Rename it as you like.
2. Create a `waves/` directory beside it.
3. Set the plugin's **`lab_path`** user config to that file. The skill reads it at
   step 0b, keeps it out of every run's allowed paths, and passes it to the tool.

The tool accepts either the lab **file** or the **directory** holding it, and looks
for `waves/` beside it. Point it at the file: that is the type the config field
takes, and it is the path a human recognises.

The tool can also be pointed by hand:

```
python "${CLAUDE_PLUGIN_ROOT}/tools/wave_stats.py" --lab <your lab dir> ledger
```

or through the `KAI_CRITIC_LAB` environment variable.

> **Never put the lab in a run's allowed paths, and never inline it.** It holds
> the hypotheses under test and the lens ledger; an agent that reads them stops
> being their test and starts playing to the scoreboard. The desk is the file the
> agent may read — it teaches how to look. The lab measures whether the looking
> worked, and it stays behind the agent's back.

## The wave record

One YAML file per wave in `<lab>/waves/W<NN>.yaml`, written by the main thread in
§6 after the owner has ruled. It is the **source of truth for every number in the
lab**: the ledger row, the three ratios, the per-lens yield and the cross-wave
medians are all computed from it, and none of them is ever counted by hand.

`wave_template.yaml` beside this file is a filled-in example. The fields:

| Field | What it holds |
|---|---|
| `wave`, `date` | the wave's id and when it ran |
| `object`, `mode`, `effort` | as given to the lenses: `design`/`strategy`/`instruction`, `blind`/`grounded`, `normal`/`enhanced`/`experimental` |
| `charter_version` | **the charter the lenses actually ran under** — this is what separates eras; the tool refuses to pool numbers across a charter change |
| `note`, `paths` | optional pointers for whoever reads the lab later |
| `tokens.total`, `tokens.by_arm` | cost; per-arm only on experimental waves |
| `runs[]` | one entry per **run**, not per lens — at `enhanced` a lens runs twice and the two runs are the measurement. Each carries `lens`, optional `arm` and `model`, `raw_findings` (what it returned before any merging) and `topics` (the topic ids it named, after its own restatements were merged) |
| `findings[]` | one entry per finding **after** the merge: `topic`, `from` (the runs that named it), `severity`, `axis`, `status`, and — once the owner has ruled — `predicted`, `ruling`, `fix` |

Two fields carry protection rather than data:

- **`status: removed` with `removed_reason`.** A finding the main thread refuted
  before showing it leaves every denominator but stays visible. Without this the
  removal would silently flatter the precision it is measured against.
- **`from`.** It ties a finding to the runs that named it, which is what makes a
  topic's uniqueness computable. A run id that does not exist is a validation
  error, not a smaller number.

A finding of the main thread's own — outside the lenses — carries `from: []`. Its
topic belongs to no run, and it counts toward no lens's uniqueness.

## The numbers

```
python tools/wave_stats.py --lab <dir> check [W22]   # validate, or validate all
python tools/wave_stats.py --lab <dir> stats W22     # one wave, shaped as a ledger row
python tools/wave_stats.py --lab <dir> ledger        # every wave, one table
python tools/wave_stats.py --lab <dir> median        # median unique topics per lens
```

**The three ratios are all computed over findings the owner actually saw**, never
over the raw pile:

- **precision** = accepted ÷ ruled on. `accept`, `accept_with_correction`,
  `downgrade` and `into_task` all count as accepted: a downgrade does not deny the
  finding, and a deferral is an acceptance that landed in other work.
- **triage agreement** = predictions that matched ÷ findings carrying both a
  prediction and a ruling. A finding whose prediction was never written leaves the
  denominator rather than counting as a miss.
- **fix hit rate** = the owner took one of your fixes ÷ accepted-and-not-deferred
  findings with a fix recorded. Rejected findings needed no fix; deferred ones got
  a task instead of one.

**Per lens:** runs, raw findings, topics, **unique topics** (topics no *other lens*
gave — not merely the ones its own second run missed), core (topics every run of
that lens found), mean pairwise Jaccard between its runs, and coverage of one run
against the lens's union.

**Per arm**, on experimental waves: accepted findings, tokens, accepted per
million, and — when the wave has a topic matrix — topics and topics unique to that
arm. **A finding counts for an arm when at least one of that arm's runs is in its
`from`.** A merged finding therefore counts for both arms, and the per-arm sums
legitimately exceed the number of findings shown. The rule is stated here because
the first wave measured without it produced a per-arm count nobody could
reproduce, and it was out by one.

**Across waves:** the median of unique topics per lens, split by charter era. A
wave with no topic matrix — a backfilled one, typically — is named and left out
rather than silently thinning the median.

## What the layer does not do

It does not decide that two differently-worded findings are the same topic, and it
does not assign topics: that is judgment and it stays with the agent. It does not
write to the lab — it prints the row and the main thread places it. It does not
read the lenses' output directly: that passes through the agent's reading, because
parsing another agent's markdown as a source of truth would restore the same
fragility from the other side.

## Guard

```
python tools/test_wave_stats.py
```

Plain python, no framework. Every test in it protects a number a human would read
as a fact and act on — a denominator off by one does not raise, it prints a
plausible ratio.
