#!/usr/bin/env python3
"""Deterministic number layer for the Critic's lab.

Every number the run protocol asks for -- the main thread's ratios, the per-run
and per-lens yield, the topic overlaps, the cross-wave median a charter hypothesis
is judged on -- is arithmetic over one structured record per wave. This module
owns that arithmetic so the main thread never retypes a count into prose.

Two texts decide what a wave's numbers mean, and a record names both. The
CHARTER decides what the lenses return (raw findings, topics, unique topics). The
SKILL decides what the main thread asks the owner and therefore what its ratios
measure. A change to either cuts its own numbers off from every wave before it,
and leaves the other's alone.

What stays with the agent: deciding that two differently-worded findings are the
same topic, whether a refutation held, whether a finding is real. What comes here:
everything downstream of those decisions.

The lab is optional infrastructure and lives in YOUR repository, not in this
plugin -- a plugin update replaces its own directory, so records kept here would
be destroyed. Point the tool at your lab with ``--lab``, or set the plugin's
``lab_path`` user config and let the skill pass it. Wave records are read from
``<lab>/waves/W*.yaml``; the schema is in ``lab/README.md`` beside the template.

Usage::

    python tools/wave_stats.py --lab <dir> check [W22]   # validate a record, or all
    python tools/wave_stats.py --lab <dir> stats W22     # one wave, ledger-row shaped
    python tools/wave_stats.py --lab <dir> ledger        # every wave, one table
    python tools/wave_stats.py --lab <dir> median        # median unique topics per lens

Exit codes: 0 fine, 1 a record failed validation, 2 usage or missing lab.
"""

from __future__ import annotations

import argparse
import os
import statistics
import sys
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment problem, not a logic one
    print("нужен pyyaml: pip install pyyaml", file=sys.stderr)
    raise SystemExit(2)

# This prints em-dashes and Cyrillic to whatever pipe the caller gives it, and the
# caller is usually an agent running it through a console with a legacy codepage.
sys.stdout.reconfigure(encoding="utf-8")

LENSES = ("beneficiary", "adversary", "auditor")
MODES = ("blind", "grounded")
OBJECTS = ("design", "strategy", "instruction")
EFFORTS = ("normal", "enhanced", "experimental")

# ---- the truth-question era: skill before 0.9.0 --------------------------------
# The owner was asked "is it true?". A ruling that counts as him agreeing the
# finding was real: `into_task` is an acceptance that lands in planned work rather
# than in this object, and a downgrade lowers severity without denying the finding.
RULINGS = ("accept", "accept_with_correction", "downgrade", "into_task", "reject")
ACCEPTING = ("accept", "accept_with_correction", "downgrade", "into_task")

# Whose repair the owner took. `mine` is the only one that scores.
FIXES = ("mine", "own", "none")

# ---- the usefulness era: skill 0.9.0 and later ---------------------------------
# Findings are shown in two blocks: the owner's (a decision about what a person
# sees or gets) and the main thread's own (mechanism only, shown as a row he may
# correct).
BLOCKS = ("owner", "agent")

# The owner's first answer, best first: the finding changed a decision, refined
# one, or he would have lost nothing without it. Truth is no longer asked -- it
# is the main thread's verification, and a ratio built on "you checked, so yes"
# saturates and measures the checker.
USEFUL = ("changed", "refined", "noise")

# His second answer. `until_shown` is "I will know when I see it": not an
# acceptance, not a rejection, and not a downgrade -- the finding stays open.
DECISIONS = ("fix", "no_fix", "into_task", "until_shown")

# `delegated` is "your choice". He chose nobody's repair, so it says nothing
# about the repertoire and leaves the fix-hit denominator; counted as `mine` it
# flattered that ratio on the wave that prompted the split.
FIXES_V2 = ("mine", "own", "delegated", "none")

# What became of a main-thread decision once he had returned the file. Silence is
# assent, so `accepted` is written by the main thread for every uncorrected row.
CORRECTIONS = ("accepted", "amended", "overturned")

# The charter version that removed the seven-finding cap. Waves under an earlier
# charter are a different population and are reported apart: comparing across a
# charter change is exactly what such a change makes illegal.
CAP_LIFTED_IN = (0, 6, 0)

# The skill version that replaced "is it true?" with "was it useful?". The main
# thread's ratios on either side of it answer different questions and never share
# a table, let alone an average. Lens-side numbers are untouched by it.
USEFULNESS_FROM = (0, 9, 0)


def _version_tuple(v: str) -> tuple[int, ...]:
    try:
        return tuple(int(p) for p in str(v).split("."))
    except ValueError:
        return (0,)


class WaveError(Exception):
    """A wave record, or a lab, that cannot be trusted to produce numbers."""


@dataclass
class Run:
    id: str
    lens: str
    topics: set[str]
    raw_findings: int
    arm: str | None = None
    model: str | None = None


@dataclass
class Finding:
    id: str
    topic: str | None
    frm: list[str]
    severity: str | None = None
    axis: str | None = None
    status: str = "shown"
    removed_reason: str | None = None
    predicted: str | None = None
    ruling: str | None = None
    fix: str | None = None
    # usefulness era only
    block: str | None = None
    predicted_useful: str | None = None
    useful: str | None = None
    correction: str | None = None
    returned: bool = False


@dataclass
class Wave:
    id: str
    path: Path
    raw: dict
    runs: list[Run] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)

    @property
    def charter(self) -> str:
        return str(self.raw.get("charter_version", "0.0.0"))

    @property
    def capped(self) -> bool:
        """True when this wave ran under a charter that still capped findings."""
        return _version_tuple(self.charter) < CAP_LIFTED_IN

    @property
    def skill(self) -> str:
        """The skill text the main thread worked under. Records written before
        the field existed carry `charter_version` alone -- the two were one
        number then, and nothing in those records depends on telling them apart."""
        return str(self.raw.get("skill_version") or self.charter)

    @property
    def usefulness_era(self) -> bool:
        """True when the owner was asked "was it useful?" rather than "is it
        true?" -- which decides both the vocabulary a record may use and which
        ratios can be computed from it."""
        return _version_tuple(self.skill) >= USEFULNESS_FROM

    @property
    def has_topics(self) -> bool:
        """A backfilled wave carries rulings but no topic matrix; say so rather
        than letting it silently thin a median."""
        return any(r.topics for r in self.runs)


# ------------------------------------------------------------------- locating


def resolve_waves_dir(lab: str | os.PathLike | None) -> Path:
    """Find the wave records. ``lab`` may be the lab directory or the lab file."""
    raw = lab or os.environ.get("KAI_CRITIC_LAB")
    if not raw:
        raise WaveError(
            "не указана лаборатория: передай --lab <каталог>, либо задай переменную "
            "KAI_CRITIC_LAB, либо настрой `lab_path` в конфиге плагина"
        )
    p = Path(raw).expanduser()
    if p.is_file():
        p = p.parent
    if not p.is_dir():
        raise WaveError(f"каталог лаборатории не найден: {p}")
    waves = p / "waves"
    if not waves.is_dir():
        raise WaveError(
            f"нет каталога записей волн: {waves}\n"
            "заведи его и положи первую запись — образец в lab/wave_template.yaml"
        )
    return waves


# --------------------------------------------------------------------- loading


def parse(doc: dict, path: Path | None = None) -> Wave:
    wave = Wave(id=str(doc.get("wave", "?")), path=path or Path("<inline>"), raw=doc)
    for r in doc.get("runs") or []:
        wave.runs.append(
            Run(
                id=str(r.get("id", "?")),
                lens=str(r.get("lens", "?")),
                topics=set(r.get("topics") or []),
                raw_findings=int(r.get("raw_findings") or 0),
                arm=r.get("arm"),
                model=r.get("model"),
            )
        )
    for f in doc.get("findings") or []:
        wave.findings.append(
            Finding(
                id=str(f.get("id", "?")),
                topic=f.get("topic"),
                frm=list(f.get("from") or []),
                severity=f.get("severity"),
                axis=f.get("axis"),
                status=str(f.get("status", "shown")),
                removed_reason=f.get("removed_reason"),
                predicted=f.get("predicted"),
                ruling=f.get("ruling"),
                fix=f.get("fix"),
                block=f.get("block"),
                predicted_useful=f.get("predicted_useful"),
                useful=f.get("useful"),
                correction=f.get("correction"),
                returned=bool(f.get("returned")),
            )
        )
    return wave


def load(wave_id: str, waves_dir: Path) -> Wave:
    path = waves_dir / f"{wave_id}.yaml"
    if not path.exists():
        raise WaveError(f"нет записи волны: {path}")
    return parse(yaml.safe_load(path.read_text(encoding="utf-8")) or {}, path)


def load_all(waves_dir: Path) -> list[Wave]:
    waves = [
        parse(yaml.safe_load(p.read_text(encoding="utf-8")) or {}, p)
        for p in sorted(waves_dir.glob("W*.yaml"))
    ]
    waves.sort(key=lambda w: int("".join(c for c in w.id if c.isdigit()) or 0))
    return waves


# ------------------------------------------------------------------ validation


def validate(wave: Wave) -> list[str]:
    """Return every problem found. An empty list means the numbers can be trusted.

    Referential integrity matters more than it looks: a `from:` naming a run that
    does not exist, or a finding whose topic no run reported, each produce a
    plausible number rather than an error.
    """
    problems: list[str] = []
    doc = wave.raw

    for key in ("wave", "date", "charter_version"):
        if not doc.get(key):
            problems.append(f"нет обязательного поля `{key}`")
    for key, allowed in (("mode", MODES), ("object", OBJECTS), ("effort", EFFORTS)):
        val = doc.get(key)
        if val is not None and val not in allowed:
            problems.append(f"`{key}: {val}` — допустимо только {'/'.join(allowed)}")
    # Agent definitions are snapshotted at session start and the skill is read at
    # invocation, so one session can run an old charter under a new skill. From
    # the version where that distinction began to matter, the record says both.
    if not doc.get("skill_version") and _version_tuple(wave.charter) >= USEFULNESS_FROM:
        problems.append(
            "нет `skill_version` — с 0.9.0 запись называет и чартер линз, и скилл "
            "главного потока: числа главного потока сравнимы только внутри одной "
            "версии скилла"
        )

    run_ids = [r.id for r in wave.runs]
    if len(set(run_ids)) != len(run_ids):
        problems.append("повторяющиеся id прогонов")
    if not wave.runs:
        problems.append("ни одного прогона в `runs`")

    for r in wave.runs:
        if r.lens not in LENSES:
            problems.append(
                f"прогон {r.id}: `lens: {r.lens}` — допустимо только {'/'.join(LENSES)}"
            )
        if r.raw_findings < len(r.topics):
            problems.append(
                f"прогон {r.id}: сырых находок {r.raw_findings} меньше, чем тем "
                f"{len(r.topics)} — темы получаются из находок, меньше быть не может"
            )

    known_runs = set(run_ids)
    seen: set[str] = set()
    for f in wave.findings:
        if f.id in seen:
            problems.append(f"находка {f.id}: повторяющийся id")
        seen.add(f.id)
        for src in f.frm:
            if src not in known_runs:
                problems.append(f"находка {f.id}: `from: {src}` — такого прогона нет")
        # A finding with an empty `from` is the main thread's own, outside the
        # lenses -- its topic belongs to nobody's run by construction. A finding
        # that DOES name runs must carry a topic one of them actually reported;
        # otherwise the attribution is wrong and every uniqueness count below it
        # is quietly wrong too. A wave with no topic matrix at all (a backfill of
        # a run that predates the record) has nothing to check against, and
        # inventing a matrix to satisfy the check would be worse than skipping it.
        if f.topic and f.frm and wave.has_topics:
            named = set().union(*(r.topics for r in wave.runs if r.id in set(f.frm))) or set()
            if f.topic not in named:
                problems.append(
                    f"находка {f.id}: тема {f.topic} не названа ни одним из прогонов "
                    f"{', '.join(f.frm)} — атрибуция расходится с `topics:` прогона"
                )
        if f.status not in ("shown", "removed"):
            problems.append(f"находка {f.id}: `status: {f.status}` — допустимо shown/removed")
        if f.status == "removed" and not f.removed_reason:
            problems.append(
                f"находка {f.id}: снята без `removed_reason` — снимает только прогнанное "
                "опровержение, и оно записывается"
            )
        if f.status == "removed" and (f.ruling or f.useful or f.correction):
            problems.append(f"находка {f.id}: снята до показа, но несёт вердикт владельца")
        problems.extend(
            _validate_usefulness(f) if wave.usefulness_era else _validate_truth(f)
        )
    return problems


def _vocab(f: Finding, pairs) -> list[str]:
    return [
        f"находка {f.id}: `{key}: {val}` — допустимо {'/'.join(allowed)}"
        for key, allowed in pairs
        if (val := getattr(f, key)) is not None and val not in allowed
    ]


def _validate_truth(f: Finding) -> list[str]:
    """A record of the truth-question era. A usefulness-era field in it means the
    record is mislabelled, and the ratios would be computed by the wrong rules."""
    problems = _vocab(f, (("predicted", RULINGS), ("ruling", RULINGS), ("fix", FIXES)))
    stray = [
        k for k in ("block", "useful", "predicted_useful", "correction") if getattr(f, k)
    ]
    if stray or f.returned:
        problems.append(
            f"находка {f.id}: поля {', '.join(stray) or 'returned'} принадлежат эпохе "
            "вопроса «полезна ли», а запись — эпохи «правда ли»; если волна шла по "
            "скиллу 0.9.0 или новее, укажи `skill_version`"
        )
    return problems


def _validate_usefulness(f: Finding) -> list[str]:
    problems = _vocab(
        f,
        (
            ("block", BLOCKS),
            ("predicted_useful", USEFUL),
            ("useful", USEFUL),
            ("predicted", DECISIONS),
            ("ruling", DECISIONS),
            ("fix", FIXES_V2),
            ("correction", CORRECTIONS),
        ),
    )
    if f.status != "shown":
        return problems
    if not f.block:
        problems.append(
            f"находка {f.id}: показана, но без `block` — owner (решает владелец) или "
            "agent (решил главный поток)"
        )
    if f.block == "agent":
        # The main thread's own block is measured directly -- did the decision
        # stand -- so an owner's answer or a prediction there is a record filled
        # in against the wrong block, not extra data.
        stray = [
            k for k in ("predicted_useful", "useful", "predicted", "ruling", "fix")
            if getattr(f, k)
        ]
        if stray:
            problems.append(
                f"находка {f.id}: блок agent, но несёт {', '.join(stray)} — у решённого "
                "главным потоком есть только `correction`"
            )
        if f.returned:
            problems.append(
                f"находка {f.id}: `returned: true` ставится на находке, которая уже "
                "переехала в блок owner"
            )
    if f.block == "owner":
        if f.correction:
            problems.append(
                f"находка {f.id}: блок owner, но несёт `correction` — поправка бывает "
                "только к решению главного потока"
            )
        took_a_fix = f.fix in ("mine", "own", "delegated")
        if f.ruling == "fix" and not took_a_fix:
            problems.append(
                f"находка {f.id}: `ruling: fix` без `fix` — чья починка: mine/own/delegated"
            )
        if f.ruling != "fix" and took_a_fix:
            problems.append(
                f"находка {f.id}: `fix: {f.fix}` при `ruling: {f.ruling}` — починку "
                "несёт только решение `fix`"
            )
    return problems


# ----------------------------------------------------------------- computation


def _jaccard(a: set[str], b: set[str]) -> float | None:
    union = a | b
    return len(a & b) / len(union) if union else None


def run_stats(wave: Wave) -> list[dict]:
    """Per run: what it returned, and what only it found in this wave."""
    out = []
    for r in wave.runs:
        others: set[str] = (
            set().union(*(o.topics for o in wave.runs if o.id != r.id))
            if len(wave.runs) > 1
            else set()
        )
        out.append(
            {
                "run": r.id,
                "lens": r.lens,
                "arm": r.arm,
                "model": r.model,
                "raw": r.raw_findings,
                "topics": len(r.topics),
                "unique": len(r.topics - others),
            }
        )
    return out


def lens_stats(wave: Wave) -> list[dict]:
    """Per lens: the yield the ledger row records since the cap came off.

    `unique` is topics this lens gave that no OTHER lens gave -- not merely the
    ones its own second run missed.
    """
    out = []
    for lens in LENSES:
        runs = [r for r in wave.runs if r.lens == lens]
        if not runs:
            continue
        own: set[str] = set().union(*(r.topics for r in runs))
        others: set[str] = set().union(*(r.topics for r in wave.runs if r.lens != lens)) or set()
        core = set.intersection(*(r.topics for r in runs)) if len(runs) > 1 else own
        pairs = [
            j for a, b in combinations(runs, 2) if (j := _jaccard(a.topics, b.topics)) is not None
        ]
        out.append(
            {
                "lens": lens,
                "runs": len(runs),
                "raw": sum(r.raw_findings for r in runs),
                "topics": len(own),
                "unique": len(own - others),
                "core": len(core) if len(runs) > 1 else None,
                "jaccard": round(statistics.mean(pairs), 2) if pairs else None,
                "coverage": (
                    round(statistics.mean([len(r.topics) / len(own) for r in runs]), 2)
                    if own
                    else None
                ),
            }
        )
    return out


def _counts_as_accepted(wave: Wave, f: Finding) -> bool:
    """What "accepted" means for a per-arm count, by era.

    Truth era: the owner's ruling accepted it. Usefulness era: in his block, he
    rated it anything but noise; in the main thread's block, he has returned the
    file -- an overturned decision is still a finding that was real. Unanswered
    findings count for nobody in either era.
    """
    if not wave.usefulness_era:
        return f.ruling in ACCEPTING
    if f.status != "shown":
        return False
    if f.block == "agent":
        return f.correction is not None
    return f.useful in ("changed", "refined")


def arm_stats(wave: Wave) -> list[dict]:
    """Per experimental arm, when the wave had them: the A/B comparison."""
    arms = sorted({r.arm for r in wave.runs if r.arm})
    if len(arms) < 2:
        return []
    by_arm = {a: {r.id for r in wave.runs if r.arm == a} for a in arms}
    topics = {
        a: set().union(*(r.topics for r in wave.runs if r.arm == a)) for a in arms
    }
    # Accepted-per-arm and cost-per-arm survive without a topic matrix; the
    # topic columns do not, and a reconstructed wave must print a blank there
    # rather than a zero that reads as a measurement.
    matrix = wave.has_topics
    out = []
    for arm in arms:
        others: set[str] = set().union(*(t for a, t in topics.items() if a != arm))
        tokens = ((wave.raw.get("tokens") or {}).get("by_arm") or {}).get(arm)
        mine = [f for f in wave.findings if by_arm[arm] & set(f.frm)]
        accepted = sum(1 for f in mine if _counts_as_accepted(wave, f))
        out.append(
            {
                "arm": arm,
                "topics": len(topics[arm]) if matrix else None,
                "unique": len(topics[arm] - others) if matrix else None,
                "accepted": accepted,
                # the discriminating count of the usefulness era; blank before it
                "changed": (
                    sum(1 for f in mine if f.useful == "changed")
                    if wave.usefulness_era
                    else None
                ),
                "tokens": tokens,
                "per_mtok": round(accepted / (tokens / 1_000_000), 1) if tokens else None,
                "jaccard": None,
            }
        )
    if len(arms) == 2 and matrix:
        out.append(
            {
                "arm": f"жаккар {arms[0]}/{arms[1]}",
                "topics": None,
                "unique": None,
                "accepted": None,
                "changed": None,
                "tokens": None,
                "per_mtok": None,
                "jaccard": round(_jaccard(topics[arms[0]], topics[arms[1]]) or 0, 2),
            }
        )
    return out


def _ratio(num: int, den: int) -> float | None:
    return round(num / den, 2) if den else None


def wave_stats(wave: Wave) -> dict:
    """The four counts, then the main thread's ratios under the rules of the
    wave's own skill era -- each ratio with its own denominator.

    Every ratio is computed over findings the owner actually SAW: a finding the
    main thread refuted never reached him, and counting it would let the removal
    flatter the number it is supposed to be measured against.
    """
    shown = [f for f in wave.findings if f.status == "shown"]
    removed = [f for f in wave.findings if f.status == "removed"]
    common = {
        "wave": wave.id,
        "date": wave.raw.get("date"),
        "charter": wave.charter,
        "skill": wave.skill,
        "capped": wave.capped,
        "era": "usefulness" if wave.usefulness_era else "truth",
        "raw_total": sum(r.raw_findings for r in wave.runs),
        "after_merge": len(wave.findings),
        "removed": len(removed),
        "shown": len(shown),
        "tokens": (wave.raw.get("tokens") or {}).get("total"),
    }
    era = _usefulness_ratios(shown) if wave.usefulness_era else _truth_ratios(shown)
    return {**common, **era}


def _usefulness_ratios(shown: list[Finding]) -> dict:
    """Skill 0.9.0 and later: usefulness, two agreements, fix hit rate, and what
    became of the main thread's own decisions."""
    owner = [f for f in shown if f.block == "owner"]
    agent = [f for f in shown if f.block == "agent"]

    # A blank mark is unrated, never a mark: folding blanks into "accepted" is
    # the main thread's judgment inside the owner's number.
    rated = [f for f in owner if f.useful]
    marks = {u: sum(1 for f in rated if f.useful == u) for u in USEFUL}

    both_useful = [f for f in owner if f.predicted_useful and f.useful]
    hit_useful = sum(1 for f in both_useful if f.predicted_useful == f.useful)
    both_decision = [f for f in owner if f.predicted and f.ruling]
    hit_decision = sum(1 for f in both_decision if f.predicted == f.ruling)

    # He chose between a repair of the main thread's and one of his own. "Your
    # choice" chose neither; not fixing, a task and "when I see it" chose none.
    chose = [f for f in owner if f.ruling == "fix" and f.fix in ("mine", "own")]
    took_mine = [f for f in chose if f.fix == "mine"]

    answered = [f for f in agent if f.correction]
    corrections = {c: sum(1 for f in answered if f.correction == c) for c in CORRECTIONS}

    return {
        "shown_owner": len(owner),
        "shown_agent": len(agent),
        "marks": marks,
        "rated_n": f"{len(rated)}/{len(owner)}",
        "changed": _ratio(marks["changed"], len(rated)),
        "changed_n": f"{marks['changed']}/{len(rated)}",
        "noise": _ratio(marks["noise"], len(rated)),
        "noise_n": f"{marks['noise']}/{len(rated)}",
        "agree_useful": _ratio(hit_useful, len(both_useful)),
        "agree_useful_n": f"{hit_useful}/{len(both_useful)}",
        "agree_decision": _ratio(hit_decision, len(both_decision)),
        "agree_decision_n": f"{hit_decision}/{len(both_decision)}",
        "fix_hit": _ratio(len(took_mine), len(chose)),
        "fix_hit_n": f"{len(took_mine)}/{len(chose)}",
        "delegated": sum(1 for f in owner if f.fix == "delegated"),
        "until_shown": sum(1 for f in owner if f.ruling == "until_shown"),
        "corrections": corrections,
        "answered_n": f"{len(answered)}/{len(agent)}",
        "returned": sum(1 for f in owner if f.returned),
    }


def _truth_ratios(shown: list[Finding]) -> dict:
    """Skill before 0.9.0: precision, triage agreement, fix hit rate."""
    ruled = [f for f in shown if f.ruling]
    accepted = [f for f in ruled if f.ruling in ACCEPTING]

    predicted = [f for f in shown if f.predicted and f.ruling]
    matched = [f for f in predicted if f.predicted == f.ruling]

    # A rejected finding needed no fix; a deferred one got a task instead of a
    # repair. Both are out of the denominator (skill §6).
    fixable = [
        f
        for f in ruled
        if f.ruling in ("accept", "accept_with_correction", "downgrade") and f.fix
    ]
    took_mine = [f for f in fixable if f.fix == "mine"]

    return {
        "precision": _ratio(len(accepted), len(ruled)),
        "precision_n": f"{len(accepted)}/{len(ruled)}",
        "agreement": _ratio(len(matched), len(predicted)),
        "agreement_n": f"{len(matched)}/{len(predicted)}",
        "fix_hit": _ratio(len(took_mine), len(fixable)),
        "fix_hit_n": f"{len(took_mine)}/{len(fixable)}",
    }


def median_unique(waves: list[Wave]) -> dict:
    """Median unique topics per lens, split by charter era.

    Waves with no topic matrix are counted and named, never silently dropped: a
    median quietly taken over three waves instead of ten is exactly the kind of
    plausible wrong number this layer exists to prevent.
    """
    buckets: dict[tuple[bool, str], list[int]] = {}
    skipped = [w.id for w in waves if not w.has_topics]
    for w in waves:
        if not w.has_topics:
            continue
        for row in lens_stats(w):
            buckets.setdefault((w.capped, row["lens"]), []).append(row["unique"])
    return {
        "skipped": skipped,
        "rows": [
            {
                "era": "с потолком" if capped else "без потолка",
                "lens": lens,
                "waves": len(vals),
                "median": statistics.median(vals) if vals else None,
                "values": vals,
            }
            for (capped, lens), vals in sorted(
                buckets.items(), key=lambda kv: (not kv[0][0], kv[0][1])
            )
        ],
    }


# ---------------------------------------------------------------- presentation


def _fmt(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, bool):
        return "да" if v else "нет"
    return str(v)


def _table(rows: list[dict], cols: list[tuple[str, str]]) -> str:
    if not rows:
        return "  (пусто)"
    widths = {k: max(len(h), *(len(_fmt(r.get(k))) for r in rows)) for k, h in cols}
    out = ["  " + "  ".join(h.ljust(widths[k]) for k, h in cols)]
    out.append("  " + "  ".join("-" * widths[k] for k, _ in cols))
    for r in rows:
        out.append("  " + "  ".join(_fmt(r.get(k)).ljust(widths[k]) for k, _ in cols))
    return "\n".join(out)


ERA_NAMES = {
    "truth": "вопрос «правда ли»",
    "usefulness": "вопрос «полезна ли»",
}

ERA_BOUNDARY = (
    "  Числа главного потока через эту границу не сравниваются: до скилла "
    + ".".join(map(str, USEFULNESS_FROM))
    + " владельца спрашивали,\n  правда ли находка, после — полезна ли она. Сырые "
    "находки, темы и уникальные темы линз\n  границу переживают: их задаёт чартер, "
    "а не скилл."
)


def _print_usefulness(s: dict) -> None:
    m, c = s["marks"], s["corrections"]
    print(
        f"  из них: на решение владельцу {s['shown_owner']} · "
        f"решено главным потоком {s['shown_agent']}"
    )
    print("\nЧисла главного потока (знаменатель — показанное, не сырое):")
    print(
        f"  польза            изменила решение {m['changed']} · уточнила {m['refined']} · "
        f"шум {m['noise']}  (оценено {s['rated_n']})"
    )
    print(f"  доля изменивших   {_fmt(s['changed'])}  ({s['changed_n']})")
    print(f"  доля шума         {_fmt(s['noise'])}  ({s['noise_n']})")
    print(f"  согласие: польза  {_fmt(s['agree_useful'])}  ({s['agree_useful_n']})")
    print(f"  согласие: решение {_fmt(s['agree_decision'])}  ({s['agree_decision_n']})")
    print(
        f"  попадание починок {_fmt(s['fix_hit'])}  ({s['fix_hit_n']}) · "
        f"отдано агенту {s['delegated']} · ждут показа {s['until_shown']}"
    )
    print(
        f"  решения главного потока: принято {c['accepted']} · уточнено {c['amended']} · "
        f"изменено {c['overturned']} · возвращено владельцу {s['returned']}  "
        f"(ответ получен по {s['answered_n']})"
    )


def cmd_check(args, waves_dir: Path) -> int:
    waves = [load(args.wave, waves_dir)] if args.wave else load_all(waves_dir)
    if not waves:
        print(f"нет записей волн в {waves_dir}")
        return 0
    bad = 0
    for w in waves:
        problems = validate(w)
        if problems:
            bad += 1
            print(f"{w.id}: {len(problems)} проблем")
            for p in problems:
                print(f"    - {p}")
        else:
            print(f"{w.id}: OK ({len(w.runs)} прогонов, {len(w.findings)} находок)")
    return 1 if bad else 0


def cmd_stats(args, waves_dir: Path) -> int:
    w = load(args.wave, waves_dir)
    problems = validate(w)
    if problems:
        print(f"{w.id}: запись не проходит проверку — числам верить нельзя:")
        for p in problems:
            print(f"    - {p}")
        return 1

    s = wave_stats(w)
    era = "с потолком" if s["capped"] else "без потолка"
    print(
        f"\n=== {w.id} · {s['date']} · чартер {s['charter']} ({era}) · "
        f"скилл {s['skill']} ({ERA_NAMES[s['era']]}) ===\n"
    )
    print("Четыре счёта волны:")
    print(f"  сырых от всех линз : {s['raw_total']}")
    print(f"  после сведения     : {s['after_merge']}")
    print(f"  снято опровержением: {s['removed']}")
    print(f"  показано владельцу : {s['shown']}")
    if s["era"] == "usefulness":
        _print_usefulness(s)
    else:
        print("\nТри числа (знаменатель — показанное, не сырое):")
        print(f"  precision       {_fmt(s['precision'])}  ({s['precision_n']})")
        print(f"  согласие триажа {_fmt(s['agreement'])}  ({s['agreement_n']})")
        print(f"  fix hit rate    {_fmt(s['fix_hit'])}  ({s['fix_hit_n']})")
    if s["tokens"]:
        print("  токенов         " + f"{s['tokens']:,}".replace(",", " "))

    print("\nПо прогонам:")
    print(
        _table(
            run_stats(w),
            [("run", "прогон"), ("lens", "линза"), ("arm", "рука"), ("model", "модель"),
             ("raw", "сырых"), ("topics", "тем"), ("unique", "уник")],
        )
    )
    print("\nПо линзам (столбец «уник» — чем судится снятый потолок):")
    print(
        _table(
            lens_stats(w),
            [("lens", "линза"), ("runs", "прогонов"), ("raw", "сырых"), ("topics", "тем"),
             ("unique", "уник"), ("core", "ядро"), ("jaccard", "жаккар"),
             ("coverage", "покрытие")],
        )
    )
    arms = arm_stats(w)
    if arms:
        print("\nПо рукам:")
        print(
            _table(
                arms,
                [("arm", "рука"), ("topics", "тем"), ("unique", "уник"),
                 ("accepted", "принято"), ("changed", "измен"), ("tokens", "токенов"),
                 ("per_mtok", "на млн"), ("jaccard", "жаккар")],
            )
        )
    print()
    return 0


def cmd_ledger(args, waves_dir: Path) -> int:
    waves = load_all(waves_dir)
    if not waves:
        print(f"нет записей волн в {waves_dir}")
        return 0
    rows = [wave_stats(w) for w in waves]
    head = [("wave", "волна"), ("date", "дата"), ("charter", "чартер"), ("skill", "скилл"),
            ("capped", "потолок"), ("raw_total", "сырых"), ("shown", "показ")]
    # One table per skill era, never one column through both: a precision and a
    # usefulness share side by side read as one series, and they are not.
    truth = [r for r in rows if r["era"] == "truth"]
    useful = [r for r in rows if r["era"] == "usefulness"]
    if truth:
        print(f"\n=== Все волны · {ERA_NAMES['truth']} ===\n")
        print(_table(truth, head + [("precision", "prec"), ("agreement", "согл"),
                                    ("fix_hit", "fix")]))
    if truth and useful:
        print("\n" + ERA_BOUNDARY)
    if useful:
        print(f"\n=== Все волны · {ERA_NAMES['usefulness']} ===\n")
        print(_table(useful, head + [("rated_n", "оценено"), ("changed", "измен"),
                                     ("noise", "шум"), ("agree_useful", "согл:польза"),
                                     ("agree_decision", "согл:реш"), ("fix_hit", "fix"),
                                     ("delegated", "отдано")]))
    print()
    return 0


def cmd_median(args, waves_dir: Path) -> int:
    waves = load_all(waves_dir)
    res = median_unique(waves)
    print("\n=== Медиана уникальных тем на линзу ===\n")
    print(
        _table(
            res["rows"],
            [("era", "эпоха"), ("lens", "линза"), ("waves", "волн"), ("median", "медиана"),
             ("values", "по волнам")],
        )
    )
    if res["skipped"]:
        print(f"\n  Без матрицы тем, в медиану не вошли: {', '.join(res['skipped'])}")
        print("  (запись волны есть, но `topics:` у прогонов пуст — обычно бэкфилл старой волны)")
    print("\n  Эпохи здесь — по чартеру. Правка скилла эту медиану не рвёт: темы называют")
    print("  линзы, а их текст задаёт чартер.")
    print()
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument(
        "--lab",
        help="каталог лаборатории (или путь к её файлу); записи волн ищутся в <lab>/waves/. "
        "По умолчанию — переменная окружения KAI_CRITIC_LAB",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("check", help="проверить запись волны (или все)")
    p.add_argument("wave", nargs="?")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("stats", help="числа одной волны — строка реестра")
    p.add_argument("wave")
    p.set_defaults(func=cmd_stats)

    sub.add_parser("ledger", help="все волны одной таблицей").set_defaults(func=cmd_ledger)
    sub.add_parser("median", help="медиана уникальных тем на линзу").set_defaults(func=cmd_median)

    args = ap.parse_args(argv)
    try:
        return args.func(args, resolve_waves_dir(args.lab))
    except WaveError as e:
        print(f"ошибка: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
