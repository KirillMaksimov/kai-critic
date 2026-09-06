#!/usr/bin/env python3
"""Guard for the Critic's number layer.

Every test here exists because the number it protects is one a human would read
as a fact and act on. A denominator quietly off by one does not raise; it prints
a plausible ratio. Run with plain python, no framework:

    python tools/test_wave_stats.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8")

import wave_stats as ws  # noqa: E402

FAILED: list[str] = []


def check(name: str, got, want):
    if got != want:
        FAILED.append(f"{name}: получено {got!r}, ожидалось {want!r}")


def wave(**over) -> ws.Wave:
    doc = {
        "wave": "W99",
        "date": "2026-09-07",
        "charter_version": "0.6.1",
        "mode": "grounded",
        "object": "design",
        "effort": "normal",
        "runs": [
            {"id": "ben-1", "lens": "beneficiary", "raw_findings": 5, "topics": ["T1", "T2"]},
            {"id": "adv-1", "lens": "adversary", "raw_findings": 6, "topics": ["T2", "T3"]},
            {"id": "aud-1", "lens": "auditor", "raw_findings": 4, "topics": ["T4"]},
        ],
        "findings": [],
    }
    doc.update(over)
    return ws.parse(doc)


# --------------------------------------------------------------- the three ratios

# The denominators are the whole point: a removed finding never reached the owner,
# a rejected one needed no fix, a deferred one got a task instead of a repair.
w = wave(
    findings=[
        {"id": "F1", "topic": "T1", "from": ["ben-1"], "status": "shown",
         "predicted": "accept", "ruling": "accept", "fix": "mine"},
        {"id": "F2", "topic": "T2", "from": ["ben-1", "adv-1"], "status": "shown",
         "predicted": "accept_with_correction", "ruling": "accept", "fix": "own"},
        {"id": "F3", "topic": "T3", "from": ["adv-1"], "status": "shown",
         "predicted": "accept", "ruling": "reject"},
        {"id": "F4", "topic": "T4", "from": ["aud-1"], "status": "shown",
         "predicted": "accept", "ruling": "into_task", "fix": "none"},
        {"id": "F5", "topic": "T3", "from": ["adv-1"], "status": "removed",
         "removed_reason": "прогнал опровержение: гард на месте"},
        # no prediction was written for this one -- it leaves the agreement
        # denominator and stays in precision, exactly as W21 had to be counted
        {"id": "F6", "topic": "T2", "from": ["adv-1"], "status": "shown",
         "ruling": "downgrade", "fix": "mine"},
    ]
)
s = ws.wave_stats(w)
check("четыре счёта: сырых", s["raw_total"], 15)
check("четыре счёта: после сведения", s["after_merge"], 6)
check("четыре счёта: снято", s["removed"], 1)
check("четыре счёта: показано", s["shown"], 5)
# accepted = F1, F2, F4(into_task), F6(downgrade); rejected = F3; removed never counted
check("precision", s["precision_n"], "4/5")
# predictions exist for F1..F4 only (F6 has none, F5 was removed); F1 and F4 matched?
# F1 accept==accept OK, F2 accept_with_correction vs accept MISS,
# F3 accept vs reject MISS, F4 accept vs into_task MISS
check("согласие триажа", s["agreement_n"], "1/4")
# fixable = accepted-and-not-deferred with a fix recorded: F1(mine), F2(own), F6(mine)
check("fix hit rate", s["fix_hit_n"], "2/3")

# A wave nobody has ruled on yet must print no ratio at all rather than 0.00 --
# an untriaged wave reading as a precision of zero is worse than a blank.
s0 = ws.wave_stats(wave(findings=[{"id": "F1", "topic": "T1", "from": ["ben-1"]}]))
check("без вердиктов precision пуст", s0["precision"], None)
check("без вердиктов согласие пусто", s0["agreement"], None)


# ------------------------------------------------------------------- uniqueness

rows = {r["lens"]: r for r in ws.lens_stats(w)}
# T2 sits in both beneficiary and adversary, so neither owns it
check("уникальные темы выгодоприобретателя", rows["beneficiary"]["unique"], 1)
check("уникальные темы противника", rows["adversary"]["unique"], 1)
check("уникальные темы аудитора", rows["auditor"]["unique"], 1)
check("тем у выгодоприобретателя", rows["beneficiary"]["topics"], 2)

# Two runs of one lens: the pair's overlap is the lens's core, and uniqueness is
# still measured against the OTHER lenses, not against its own second run.
w2 = wave(
    runs=[
        {"id": "adv-1", "lens": "adversary", "raw_findings": 8, "topics": ["T1", "T2", "T3"]},
        {"id": "adv-2", "lens": "adversary", "raw_findings": 7, "topics": ["T2", "T9"]},
        {"id": "ben-1", "lens": "beneficiary", "raw_findings": 5, "topics": ["T3"]},
    ]
)
adv = {r["lens"]: r for r in ws.lens_stats(w2)}["adversary"]
check("два прогона: тем у линзы", adv["topics"], 4)          # T1,T2,T3,T9
check("два прогона: ядро", adv["core"], 1)                    # T2
check("два прогона: уникальные против других линз", adv["unique"], 3)  # T3 отдан
check("два прогона: жаккар", adv["jaccard"], 0.25)            # |{T2}| / |{T1,T2,T3,T9}|

runs = {r["run"]: r for r in ws.run_stats(w2)}
check("уникальность прогона внутри волны", runs["adv-2"]["unique"], 1)  # T9


# ------------------------------------------------------------------- validation

# Every one of these produces a plausible NUMBER when it slips through, which is
# why they are errors and not warnings.
bad = wave(
    runs=[{"id": "adv-1", "lens": "противник", "raw_findings": 1, "topics": ["T1", "T2"]}],
    findings=[
        {"id": "F1", "topic": "T9", "from": ["ghost-1"], "ruling": "yes"},
        {"id": "F1", "topic": "T1", "from": ["adv-1"], "status": "removed"},
    ],
)
problems = " | ".join(ws.validate(bad))
for fragment, label in [
    ("lens: противник", "неизвестная линза"),
    ("такого прогона нет", "ссылка на несуществующий прогон"),
    ("сырых находок 1 меньше, чем тем 2", "тем больше, чем находок"),
    ("повторяющийся id", "дубль id находки"),
    ("ruling: yes", "неизвестный вердикт"),
    ("removed_reason", "снятие без причины"),
]:
    if fragment not in problems:
        FAILED.append(f"валидация не поймала: {label}")

# A main-thread finding belongs to no run, so its topic is nobody's -- that must
# pass, or every wave with an out-of-lens finding fails validation.
own = wave(findings=[{"id": "F1", "topic": "T77", "from": [], "status": "shown",
                      "ruling": "accept", "fix": "mine"}])
check("своя находка вне линз проходит", ws.validate(own), [])

# But a finding that DOES name a run must carry a topic that run reported.
misattributed = wave(findings=[{"id": "F1", "topic": "T4", "from": ["ben-1"]}])
check(
    "расхождение атрибуции ловится",
    any("атрибуция расходится" in p for p in ws.validate(misattributed)),
    True,
)

check("правильная запись проходит без замечаний", ws.validate(w), [])


# ------------------------------------------------------------------- the median

capped = wave(charter_version="0.5.1")
uncapped = wave(charter_version="0.6.1")
backfill = wave(
    charter_version="0.4.0",
    runs=[{"id": "adv-1", "lens": "adversary", "raw_findings": 7, "topics": []}],
)
check("волна с потолком опознана", capped.capped, True)
check("волна без потолка опознана", uncapped.capped, False)

res = ws.median_unique([capped, uncapped, backfill])
check("бэкфилл без тем назван, а не выброшен молча", res["skipped"], ["W99"])
eras = {(r["era"], r["lens"]): r for r in res["rows"]}
check("эпохи не смешиваются", len(eras), 6)
check("медиана считается по своей эпохе", eras[("без потолка", "adversary")]["median"], 1)


# ----------------------------------------------------------------------- result

if FAILED:
    print(f"ПРОВАЛЕНО {len(FAILED)}:")
    for f in FAILED:
        print("  -", f)
    raise SystemExit(1)
print("все проверки пройдены")
