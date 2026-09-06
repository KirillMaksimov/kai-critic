#!/usr/bin/env python3
"""Deterministic number layer for the Critic's lab.

Every number the run protocol asks for -- the three ratios, the per-run and
per-lens yield, the topic overlaps, the cross-wave median a charter hypothesis is
judged on -- is arithmetic over one structured record per wave. This module owns
that arithmetic so the main thread never retypes a count into prose.

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

# A ruling that counts as the owner agreeing the finding was real. `into_task` is
# an acceptance that lands in planned work rather than in this object (skill §5),
# and a downgrade lowers severity without denying the finding -- both count.
RULINGS = ("accept", "accept_with_correction", "downgrade", "into_task", "reject")
ACCEPTING = ("accept", "accept_with_correction", "downgrade", "into_task")

# Whose repair the owner took. `mine` is the only one that scores.
FIXES = ("mine", "own", "none")

# The charter version that removed the seven-finding cap. Waves under an earlier
# charter are a different population and are reported apart: comparing across a
# charter change is exactly what such a change makes illegal.
CAP_LIFTED_IN = (0, 6, 0)


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
        if f.status == "removed" and f.ruling:
            problems.append(f"находка {f.id}: снята до показа, но несёт вердикт владельца")
        for key, allowed in (("predicted", RULINGS), ("ruling", RULINGS), ("fix", FIXES)):
            val = getattr(f, key)
            if val is not None and val not in allowed:
                problems.append(f"находка {f.id}: `{key}: {val}` — допустимо {'/'.join(allowed)}")
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
        accepted = sum(
            1
            for f in wave.findings
            if f.ruling in ACCEPTING and by_arm[arm] & set(f.frm)
        )
        out.append(
            {
                "arm": arm,
                "topics": len(topics[arm]) if matrix else None,
                "unique": len(topics[arm] - others) if matrix else None,
                "accepted": accepted,
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
                "tokens": None,
                "per_mtok": None,
                "jaccard": round(_jaccard(topics[arms[0]], topics[arms[1]]) or 0, 2),
            }
        )
    return out


def wave_stats(wave: Wave) -> dict:
    """The four counts and the three ratios, each with its own denominator.

    All three are computed over findings the owner actually SAW: a finding the
    main thread refuted never reached him, and counting it would let the removal
    flatter the precision it is supposed to be measured against.
    """
    shown = [f for f in wave.findings if f.status == "shown"]
    removed = [f for f in wave.findings if f.status == "removed"]

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

    def ratio(num: int, den: int) -> float | None:
        return round(num / den, 2) if den else None

    return {
        "wave": wave.id,
        "date": wave.raw.get("date"),
        "charter": wave.charter,
        "capped": wave.capped,
        "raw_total": sum(r.raw_findings for r in wave.runs),
        "after_merge": len(wave.findings),
        "removed": len(removed),
        "shown": len(shown),
        "precision": ratio(len(accepted), len(ruled)),
        "precision_n": f"{len(accepted)}/{len(ruled)}",
        "agreement": ratio(len(matched), len(predicted)),
        "agreement_n": f"{len(matched)}/{len(predicted)}",
        "fix_hit": ratio(len(took_mine), len(fixable)),
        "fix_hit_n": f"{len(took_mine)}/{len(fixable)}",
        "tokens": (wave.raw.get("tokens") or {}).get("total"),
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
    print(f"\n=== {w.id} · {s['date']} · чартер {s['charter']} ({era}) ===\n")
    print("Четыре счёта волны:")
    print(f"  сырых от всех линз : {s['raw_total']}")
    print(f"  после сведения     : {s['after_merge']}")
    print(f"  снято опровержением: {s['removed']}")
    print(f"  показано владельцу : {s['shown']}")
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
                 ("accepted", "принято"), ("tokens", "токенов"), ("per_mtok", "на млн"),
                 ("jaccard", "жаккар")],
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
    print("\n=== Все волны ===\n")
    print(
        _table(
            rows,
            [("wave", "волна"), ("date", "дата"), ("charter", "чартер"), ("capped", "потолок"),
             ("raw_total", "сырых"), ("shown", "показ"), ("precision", "prec"),
             ("agreement", "согл"), ("fix_hit", "fix")],
        )
    )
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
