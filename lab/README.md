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
§6 — the runs and the findings before the owner has answered, his answers once he
has. It is the **source of truth for every number in the lab**: the ledger row,
the main thread's ratios, the per-lens yield and the cross-wave medians are all
computed from it, and none of them is ever counted by hand.

`wave_template.yaml` beside this file is a filled-in example. The fields:

| Field | What it holds |
|---|---|
| `wave`, `date` | the wave's id and when it ran |
| `object`, `mode`, `effort` | as given to the lenses: `design`/`strategy`/`instruction`, `blind`/`grounded`, `normal`/`enhanced`/`experimental` |
| `charter_version` | **the charter the lenses actually ran under** — it decides what they return, and it separates the eras of the lens-side numbers |
| `skill_version` | **the skill the main thread worked under** — it decides what the owner is asked, and it separates the eras of the main thread's ratios. Required from 0.9.0; a record without it is read as the era before. From 0.10.0 usefulness is rated on four ranks, before it on three |
| `useful_scale` | optional, `4` only: the owner rated on four ranks while an older skill still asked on three. His marks are what the record keeps; without the field the skill version decides |
| `note`, `paths` | optional pointers for whoever reads the lab later |
| `tokens.total`, `tokens.by_arm` | subagent cost; per-arm only on experimental waves |
| `main_thread` | optional, from 0.13.0: the main thread's own half — `duration_ms` (launch of the topic pass to the review file on disk, from two timestamps) and `tokens` (only when the host reports the session's usage). Either is left out rather than guessed |
| `authored_in_session` | optional, from 0.13.0: `true` when the session that ran the wave also wrote the object — the authorship confound. `ledger` shows it beside the wave |
| `appendix_read` | optional, from 0.17.0: a list of the owner's statements that he read rows of the appendix — `where` (`chat` or `file`), `date`, `quote` (his words, verbatim) and `rows` (`all`, meaning every appendix row he did not correct, or their ids). A row it covers that he left uncorrected is **accepted on his word**, counted apart from the body's accepted and from the unread. Never inferred, never asked for; `check` refuses one without a quote, one naming a row outside the appendix or a corrected row, and one that covers nothing |
| `topic_pass` | the topic pass that ran before the lenses: `model`, `runs`, `topics` — one entry per arm when the arms differ there, `runs: 0` for an arm that ran without one. It says which lens-side numbers compare, since the lenses read its list: `median` splits by its model. A record without it is legal and forms a series of its own; a per-arm record that leaves out a run's arm is refused by `check` |
| `runs[]` | one entry per **run**, not per lens — at `enhanced` a lens runs twice and the two runs are the measurement. Each carries `lens`, optional `arm` and `model`, `raw_findings` (what it returned before any merging) and `topics` (the topic ids it named, after its own restatements were merged); `extra_topics` when a finding it returned carried more than one topic — never a split of `raw_findings` |
| `findings[]` | one entry per finding **after** the merge: `topic`, `from` (the runs that named it), `severity`, `axis`, `reach` (from 0.12.0: "N of M …" / «N из M …», whole object, or not counted), `status`, `block`, and — once the owner has answered — his answers beside the main thread's predictions (below) |

What a shown finding carries depends on its `block` — who decided it (skill §5,
step 2):

| `block` | Fields | Values |
|---|---|---|
| `owner` — ruling on it meant choosing what a person sees or gets | `predicted_useful`, `useful` | `changed` (a decision the design had taken is different after it) · `extended` (the design stands, but a feature is added or what a person observes reaches further — from 0.10.0) · `refined` (a small precision that changes nothing a person observes) · `noise` (unimportant, does not affect the delivery). **His mark; a blank is left out, never guessed** |
| | `predicted`, `ruling` | `fix` · `no_fix` · `into_task` · `until_shown` ("I will know when I see it" — the finding stays open) |
| | `fix` | `mine` · `own` · `delegated` ("your choice") · `none`. Only a `ruling: fix` carries a repair |
| | `returned: true` | he took this row back from the main thread's block |
| `agent` — every sensible fix gave a person the same thing; the main thread decided | `correction` | `accepted` (no correction on a row in the **body** — silence is assent there once he has returned the file) · `amended` (the decision stands, made more exact) · `overturned` (a different decision replaces it). Left out until he has answered, and left out for good on an appendix row he did not correct |
| | `placed` | from skill 0.14.0: `appendix` for a row that did not need him and stood in the appendix; absent means the body. An appendix row without a correction is **unread** unless the wave's `appendix_read` covers it, and `check` refuses `accepted` on it either way |

Two fields carry protection rather than data:

- **`status: removed` with `removed_reason`.** A finding the main thread refuted
  before showing it leaves every denominator but stays visible. Without this the
  removal would silently flatter the numbers it is measured against. A reason
  that opens with `outside the delivery` marks a set-aside by the owner's
  standing ruling (skill 0.12.0) rather than a refutation, and `stats` counts the
  two apart.
- **`from`.** It ties a finding to the runs that named it, which is what makes a
  topic's uniqueness computable. A run id that does not exist is a validation
  error, not a smaller number.

A finding of the main thread's own — outside the lenses — carries `from: []`. Its
topic belongs to no run, and it counts toward no lens's uniqueness.

## Two eras, two axes

Two texts decide what a wave's numbers mean. **The charter** decides what the
lenses return — raw findings, topics, unique topics. **The skill** decides what
the main thread asks the owner — and so what its ratios measure. A change to
either cuts *its* numbers off from every wave before it, and leaves the other's
alone. That is why a record names both versions, and why they can differ inside
one session: agent definitions are snapshotted when the session starts, the skill
is read when it is invoked.

| Boundary | What it cut | What survives it |
|---|---|---|
| charter 0.6.0 — the cap on findings per lens came off | raw findings, topics, unique topics per lens; `median` reports the two sides apart | — |
| skill 0.9.0 — "is it true?" became "was it useful?" | precision, triage agreement, fix hit rate: `stats` computes each record by the rules of its own era, and `ledger` prints one table per era with the boundary named between them | everything lens-side, the `median` included — the charter did not move |
| every later change of the text the lenses read — 0.9.2, 0.10.2, 0.11.0, 0.12.0 (`LENS_TEXT_CHANGES` in the tool) | lens-side numbers across it: from 0.13.0 `median` splits its series by the lens text a record ran under, as skill step 0c always said it should | the main thread's ratios |
| skill 0.10.0 — four ranks of usefulness; the topic pass of a `normal` run moved from Sonnet to Opus | the shares of usefulness and the agreement on usefulness (`ledger` prints three and four ranks as two tables); every lens-side number across a change of topic-pass model (`median` splits by the model in `topic_pass`) | the agreement on the decision, the fix hit rate, the main thread's own decisions; lens-side numbers between waves whose topic pass ran on the same model |

**Records from before skill 0.9.0 keep their own vocabulary and stay valid as they
are**: `predicted` / `ruling` of `accept` · `accept_with_correction` · `downgrade` ·
`into_task` · `reject`, `fix` of `mine` · `own` · `none`, no `block`, no `useful`.
Do not convert them — a precision re-expressed as a usefulness share would be a
number nobody measured. `check` refuses a record that mixes the two vocabularies,
because a mislabelled record is computed by the wrong rules and prints a plausible
ratio.

## The numbers

```
python tools/wave_stats.py --lab <dir> check [W22]   # validate, or validate all
python tools/wave_stats.py --lab <dir> stats W22     # one wave, shaped as a ledger row
python tools/wave_stats.py --lab <dir> ledger        # every wave, one table
python tools/wave_stats.py --lab <dir> median        # median unique topics per lens
```

**Every ratio is computed over findings the owner actually saw**, never over the
raw pile. From skill 0.9.0:

- **usefulness** = his marks over the findings of **his block that he rated**:
  the share that `changed` a decision is the headline, the shares of `extended`
  and of `noise` stand beside it, and the count rated goes with them. It replaces
  precision, which an owner who does not read the code answers with "you checked,
  so yes" — a ratio that saturates and measures the main thread's verification,
  not the lenses. **The shares and the agreement on usefulness do not cross from
  three ranks to four**: on three, `changed` also took in what four call
  `extended`. `ledger` prints the two scales as two tables.
- **triage agreement**, twice: predicted usefulness against his mark, and
  predicted decision against his decision. A finding missing either half of a pair
  leaves that denominator rather than counting as a miss.
- **fix hit rate** = he took one of the main thread's fixes ÷ findings where he
  chose between one of those and his own. `delegated` is **out of the
  denominator** and counted beside it: he chose nobody's repair, so it says
  nothing about the repertoire — it says the finding was sorted into the wrong
  block. Not fixing, a task and "when I see it" chose no repair either.
- **the main thread's decisions** = accepted · amended · overturned, over the rows
  of its own block that stood in the body, with the rows he took back counted
  beside; the appendix is counted apart — rows, corrected, accepted on his word
  (`appendix_read`), unread. The three kinds of uncorrected row are never added
  up: `stats` prints them apart with his words under them, and `ledger` gives
  them a table of their own from 0.14.0 on. Before skill
  0.14.0 every row stood in the body, and the owner said afterwards that silence
  over twenty rows had meant he had not read them: `stats` prints those waves'
  uncorrected rows as "без поправки", not as accepted.

Before skill 0.9.0 the three were **precision** (accepted ÷ ruled on, with
`accept`, `accept_with_correction`, `downgrade` and `into_task` all accepting),
**triage agreement** (predicted ruling against his) and **fix hit rate** (`mine` ÷
accepted-and-not-deferred findings with a fix recorded). They are still computed
for those records, by those rules.

**Per lens:** runs, raw findings, topics, **unique topics** (topics no *other lens*
gave — not merely the ones its own second run missed), core (topics every run of
that lens found), mean pairwise Jaccard between its runs, and coverage of one run
against the lens's union.

**Per arm**, on experimental waves: accepted findings, tokens, accepted per
million, and — when the wave has a topic matrix — topics and topics unique to that
arm. "Accepted" follows the wave's own era: before skill 0.9.0, his ruling accepted
it; from 0.9.0, he rated it anything but `noise` in his block, or has returned the
file on a row of the main thread's block — an overturned decision is still a
finding that was real. The count that `changed` a decision is printed beside it.
**A finding counts for an arm when at least one of that arm's runs is in its
`from`.** A merged finding therefore counts for both arms, and the per-arm sums
legitimately exceed the number of findings shown. The rule is stated here because
the first wave measured without it produced a per-arm count nobody could
reproduce, and it was out by one.

**Across waves:** the median of unique topics per lens, split by charter era and
by the model of the topic pass — the lenses read its list, so their topics compare
only under one model. A skill change that leaves the launch alone does not cut it,
because topics are named by the lenses and the charter is their text. On an
experimental wave whose arms read topic passes on different models, each arm is a
point of its own series, named `W28/A`, with uniqueness measured inside the arm; a
wave with no `topic_pass` is a series of its own rather than a guess. A wave with
no topic matrix — a backfilled one, typically — is named and left out rather than
silently thinning the median.
The main thread's ratios are **never** aggregated across waves by the tool, in
either era.

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
