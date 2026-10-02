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


# ------------------------------------------------- the usefulness era (skill 0.9.0+)

# The charter did not move, the skill did: lens-side numbers stay in their era,
# the main thread's ratios start a new one.
NEW = {"charter_version": "0.8.0", "skill_version": "0.9.0"}

u = wave(
    **NEW,
    findings=[
        # the owner's block: six findings, five of them rated
        {"id": "N1", "topic": "T1", "from": ["ben-1"], "block": "owner",
         "predicted_useful": "changed", "useful": "changed",
         "predicted": "fix", "ruling": "fix", "fix": "mine"},
        {"id": "N2", "topic": "T2", "from": ["ben-1", "adv-1"], "block": "owner",
         "predicted_useful": "changed", "useful": "refined",
         "predicted": "fix", "ruling": "fix", "fix": "own"},
        # "your choice": he took nobody's repair -- out of the fix-hit denominator,
        # counted beside it. Scored as `mine` this flattered the ratio once.
        {"id": "N3", "topic": "T3", "from": ["adv-1"], "block": "owner",
         "predicted_useful": "refined", "useful": "refined",
         "predicted": "fix", "ruling": "fix", "fix": "delegated"},
        {"id": "N4", "topic": "T4", "from": ["aud-1"], "block": "owner",
         "predicted_useful": "refined", "useful": "noise",
         "predicted": "fix", "ruling": "no_fix", "fix": "none"},
        # "I will know when I see it": no mark, no repair -- unrated, never folded
        # into a mark, and out of the fix-hit denominator
        {"id": "N5", "topic": "T2", "from": ["adv-1"], "block": "owner",
         "predicted_useful": "noise", "predicted": "no_fix", "ruling": "until_shown"},
        # taken back from the main thread's block and ruled on like the rest
        {"id": "N6", "topic": "T3", "from": ["adv-1"], "block": "owner", "returned": True,
         "useful": "changed", "ruling": "into_task", "fix": "none"},
        # the main thread's block: silence is assent, a correction is one of two kinds
        {"id": "N7", "topic": "T1", "from": ["ben-1"], "block": "agent",
         "correction": "accepted"},
        {"id": "N8", "topic": "T4", "from": ["aud-1"], "block": "agent",
         "correction": "amended"},
        {"id": "N9", "topic": "T77", "from": [], "block": "agent",
         "correction": "overturned"},
        # he has not returned the file for this one yet
        {"id": "N10", "topic": "T3", "from": ["adv-1"], "block": "agent"},
        {"id": "N11", "topic": "T3", "from": ["adv-1"], "status": "removed",
         "removed_reason": "прогнал опровержение: гард на месте"},
    ],
)
check("запись эпохи пользы проходит без замечаний", ws.validate(u), [])
su = ws.wave_stats(u)
check("эпоха опознана по версии скилла", su["era"], "usefulness")
check("потолок по-прежнему судится по чартеру", su["capped"], False)
check("показано: всего", su["shown"], 10)
check("показано: блок владельца", su["shown_owner"], 6)
check("показано: блок главного потока", su["shown_agent"], 4)
check("польза: оценено", su["rated_n"], "5/6")
check("польза: по ступеням", su["marks"], {"changed": 2, "refined": 2, "noise": 1})
check("доля изменивших решение", su["changed_n"], "2/5")
check("доля шума", su["noise_n"], "1/5")
# N1 changed==changed, N3 refined==refined; N2 and N4 missed; N5 has no mark, N6
# no prediction -- both leave the denominator rather than counting as misses
check("согласие по пользе", su["agree_useful_n"], "2/4")
# N1, N2, N3 fix==fix; N4 fix vs no_fix, N5 no_fix vs until_shown missed
check("согласие по решению", su["agree_decision_n"], "3/5")
check("попадание починок: отданное агенту вне знаменателя", su["fix_hit_n"], "1/2")
check("отдано агенту", su["delegated"], 1)
check("ждут показа", su["until_shown"], 1)
check("решения главного потока", su["corrections"],
      {"accepted": 1, "amended": 1, "overturned": 1})
check("решения главного потока: ответ получен", su["answered_n"], "3/4")
check("возвращено владельцу", su["returned"], 1)
check("числа эпохи «правда ли» не печатаются", "precision" in su, False)

# The old era is untouched by all this: same record, same three numbers.
check("эпоха «правда ли» опознана", s["era"], "truth")
check("числа эпохи пользы в ней не печатаются", "marks" in s, False)

# Mixing the vocabularies is the way a record gets computed by the wrong rules.
mixed_old = wave(findings=[{"id": "F1", "topic": "T1", "from": ["ben-1"],
                            "ruling": "accept", "useful": "changed"}])
check("поле новой эпохи в старой записи ловится",
      any("принадлежат эпохе" in p for p in ws.validate(mixed_old)), True)
mixed_new = wave(**NEW, findings=[{"id": "N1", "topic": "T1", "from": ["ben-1"],
                                   "block": "owner", "ruling": "accept"}])
check("старый вердикт в новой записи ловится",
      any("ruling: accept" in p for p in ws.validate(mixed_new)), True)

bad_new = wave(
    **NEW,
    findings=[
        {"id": "N1", "topic": "T1", "from": ["ben-1"]},
        {"id": "N2", "topic": "T1", "from": ["ben-1"], "block": "agent", "useful": "noise"},
        {"id": "N3", "topic": "T1", "from": ["ben-1"], "block": "owner", "ruling": "fix"},
        {"id": "N4", "topic": "T1", "from": ["ben-1"], "block": "owner",
         "ruling": "until_shown", "fix": "mine"},
        {"id": "N5", "topic": "T1", "from": ["ben-1"], "block": "owner",
         "correction": "amended"},
    ],
)
problems = " | ".join(ws.validate(bad_new))
for fragment, label in [
    ("N1: показана, но без `block`", "показанная находка без блока"),
    ("N2: блок agent, но несёт useful", "оценка пользы в блоке главного потока"),
    ("N3: `ruling: fix` без `fix`", "решение «чинить» без починки"),
    ("N4: `fix: mine` при `ruling: until_shown`", "починка при решении без починки"),
    ("N5: блок owner, но несёт `correction`", "поправка в блоке владельца"),
]:
    if fragment not in problems:
        FAILED.append(f"валидация эпохи пользы не поймала: {label}")

# One session can run a snapshotted old charter under a new skill, so from 0.9.0
# the record names both -- a missing skill version is refused, not guessed.
unnamed = wave(charter_version="0.9.0")
check("без версии скилла с 0.9.0 запись не проходит",
      any("skill_version" in p for p in ws.validate(unnamed)), True)
legacy = wave(charter_version="0.8.0")
check("старая запись без версии скилла остаётся законной", ws.validate(legacy), [])
check("старая запись без версии скилла — эпоха «правда ли»", legacy.usefulness_era, False)

# A skill change does not move the lens-side median: topics are named by the
# lenses, and the charter, not the skill, is their text.
res2 = ws.median_unique([uncapped, u])
eras2 = {(r["era"], r["lens"]): r for r in res2["rows"]}
check("правка скилла не рвёт медиану линз", eras2[("без потолка", "adversary")]["waves"], 2)

# Per arm, "accepted" follows the wave's own era.
ab = wave(
    **NEW,
    runs=[
        {"id": "adv-a", "lens": "adversary", "arm": "A", "raw_findings": 3, "topics": ["T1", "T2"]},
        {"id": "adv-b", "lens": "adversary", "arm": "B", "raw_findings": 3, "topics": ["T2", "T3"]},
    ],
    findings=[
        {"id": "N1", "topic": "T1", "from": ["adv-a"], "block": "owner", "useful": "changed"},
        {"id": "N2", "topic": "T2", "from": ["adv-a", "adv-b"], "block": "owner",
         "useful": "noise"},
        {"id": "N3", "topic": "T3", "from": ["adv-b"], "block": "agent",
         "correction": "overturned"},
        {"id": "N4", "topic": "T3", "from": ["adv-b"], "block": "agent"},
    ],
)
arms = {r["arm"]: r for r in ws.arm_stats(ab)}
check("рука A: шум не засчитан", arms["A"]["accepted"], 1)
check("рука B: изменённое решение — находка была, без ответа — нет", arms["B"]["accepted"], 1)
check("рука A: изменивших решение", arms["A"]["changed"], 1)


# ------------------------------------------------ the topic pass's model (0.10.1+)

# The lenses read the topic pass's list, so their topics compare only between runs
# whose topic pass ran on the same model. Two uncapped waves on two models are two
# series, and a record that never said which is a third -- never a guess.
on_sonnet = wave(topic_pass={"model": "sonnet", "runs": 1, "topics": 20})
on_opus = wave(topic_pass={"model": "opus", "runs": 1, "topics": 40})
res3 = ws.median_unique([on_sonnet, on_opus, uncapped])
rows3 = {(r["era"], r.get("topic_pass"), r["lens"]): r for r in res3["rows"]}
check("модели прохода тем не смешиваются в медиане", len(rows3), 9)
for model in ("sonnet", "opus", "не записан"):
    check(f"ряд прохода тем «{model}» — одна волна",
          rows3.get(("без потолка", model, "adversary"), {}).get("waves"), 1)

# On an experimental wave whose arms differ in the topic pass, a run takes its
# arm's model, and uniqueness is measured inside the arm: pooled across the arms
# the adversary below owns one topic, while inside arm A it owns two.
split = wave(
    **NEW,
    effort="experimental",
    topic_pass={"A": {"model": "opus", "runs": 1, "topics": 40},
                "B": {"model": "sonnet", "runs": 1, "topics": 20}},
    runs=[
        {"id": "adv-A", "lens": "adversary", "arm": "A", "raw_findings": 3,
         "topics": ["T1", "T2", "T3"]},
        {"id": "ben-A", "lens": "beneficiary", "arm": "A", "raw_findings": 1, "topics": ["T1"]},
        {"id": "adv-B", "lens": "adversary", "arm": "B", "raw_findings": 1, "topics": ["T2"]},
        {"id": "ben-B", "lens": "beneficiary", "arm": "B", "raw_findings": 2,
         "topics": ["T3", "T4"]},
    ],
)
check("проход тем по рукам проходит проверку", ws.validate(split), [])
rows4 = {(r.get("topic_pass"), r["lens"]): r for r in ws.median_unique([split])["rows"]}
check("рука Opus: уникальные противника внутри руки",
      rows4.get(("opus", "adversary"), {}).get("values"), [2])
check("рука Sonnet: уникальные выгодоприобретателя внутри руки",
      rows4.get(("sonnet", "beneficiary"), {}).get("values"), [2])
check("точка ряда названа волной и рукой",
      rows4.get(("opus", "adversary"), {}).get("sources"), ["W99/A"])
# A wave whose runs all read one topic pass stays one point, named by the wave.
check("волна одним проходом — точка без руки",
      rows3.get(("без потолка", "opus", "adversary"), {}).get("sources"), ["W99"])

# An arm that ran without a topic pass says `runs: 0`: a series of its own, not
# the unrecorded one and not a model.
bare = wave(
    **NEW,
    effort="experimental",
    topic_pass={"A": {"model": "opus", "runs": 1, "topics": 40}, "B": {"runs": 0}},
    runs=[
        {"id": "adv-A", "lens": "adversary", "arm": "A", "raw_findings": 1, "topics": ["T1"]},
        {"id": "adv-B", "lens": "adversary", "arm": "B", "raw_findings": 1, "topics": ["T2"]},
    ],
)
check("рука без прохода тем проходит проверку", ws.validate(bare), [])
rows5 = {(r.get("topic_pass"), r["lens"]) for r in ws.median_unique([bare])["rows"]}
check("рука без прохода тем — свой ряд", ("не было", "adversary") in rows5, True)

# A per-arm topic pass that does not name a run's arm would drop that run into the
# unrecorded series without a word -- a plausible number, so an error.
orphan = wave(
    topic_pass={"A": {"model": "opus", "runs": 1}},
    runs=[
        {"id": "adv-A", "lens": "adversary", "arm": "A", "raw_findings": 1, "topics": ["T1"]},
        {"id": "adv-B", "lens": "adversary", "arm": "B", "raw_findings": 1, "topics": ["T2"]},
        {"id": "ben-1", "lens": "beneficiary", "raw_findings": 1, "topics": ["T3"]},
    ],
)
orphan_problems = ws.validate(orphan)
check("рука, не названная в `topic_pass`, ловится",
      any("adv-B" in p and "topic_pass" in p for p in orphan_problems), True)
check("прогон без руки при проходе по рукам ловится",
      any("ben-1" in p and "topic_pass" in p for p in orphan_problems), True)
nameless = wave(topic_pass={"runs": 1, "topics": 20})
check("проход тем без модели ловится",
      any("topic_pass" in p and "model" in p for p in ws.validate(nameless)), True)


# ------------------------------------------------ four ranks of usefulness (0.10.0+)

# "Extended" is a rank of its own from 0.10.0. Under three ranks it read as
# "changed", so the two scales never share a column.
FOUR = {"charter_version": "0.9.2", "skill_version": "0.10.0"}
four = wave(
    **FOUR,
    findings=[
        {"id": "N1", "topic": "T1", "from": ["ben-1"], "block": "owner",
         "predicted_useful": "changed", "useful": "changed",
         "predicted": "fix", "ruling": "fix", "fix": "mine"},
        {"id": "N2", "topic": "T2", "from": ["adv-1"], "block": "owner",
         "predicted_useful": "refined", "useful": "extended",
         "predicted": "fix", "ruling": "fix", "fix": "mine"},
        {"id": "N3", "topic": "T3", "from": ["adv-1"], "block": "owner",
         "predicted_useful": "extended", "useful": "extended",
         "predicted": "fix", "ruling": "fix", "fix": "own"},
        {"id": "N4", "topic": "T4", "from": ["aud-1"], "block": "owner",
         "predicted_useful": "refined", "useful": "noise",
         "predicted": "fix", "ruling": "no_fix", "fix": "none"},
    ],
)
check("запись на четырёх ступенях проходит", ws.validate(four), [])
check("четыре ступени опознаны по версии скилла", four.useful_scale, 4)
sf = ws.wave_stats(four)
check("четыре ступени: по ступеням", sf["marks"],
      {"changed": 1, "extended": 2, "refined": 0, "noise": 1})
check("доля расширивших", sf["extended_n"], "2/4")
check("доля изменивших не вбирает расширивших", sf["changed_n"], "1/4")
check("согласие по пользе: «уточнила» против «расширила» — промах",
      sf["agree_useful_n"], "2/4")
check("на трёх ступенях «расширила» не печатается нулём", "extended" in su["marks"], False)
check("на трёх ступенях доли расширивших нет", su["extended_n"], None)

# Per arm, "extended" is not noise, so it is accepted.
ab4 = wave(
    **FOUR,
    runs=[{"id": "adv-a", "lens": "adversary", "arm": "A", "raw_findings": 1, "topics": ["T1"]},
          {"id": "adv-b", "lens": "adversary", "arm": "B", "raw_findings": 1, "topics": ["T2"]}],
    findings=[{"id": "N1", "topic": "T1", "from": ["adv-a"], "block": "owner",
               "useful": "extended"},
              {"id": "N2", "topic": "T2", "from": ["adv-b"], "block": "owner",
               "useful": "noise"}],
)
arms4 = {r["arm"]: r for r in ws.arm_stats(ab4)}
check("рука: «расширила» засчитана как принятая", arms4["A"]["accepted"], 1)

# The vocabulary of four ranks in a three-rank record is the wrong scale.
three_ext = wave(**NEW, findings=[{"id": "N1", "topic": "T1", "from": ["ben-1"],
                                   "block": "owner", "useful": "extended"}])
check("«расширила» на трёх ступенях ловится",
      any("useful: extended" in p for p in ws.validate(three_ext)), True)
three_pred = wave(**NEW, findings=[{"id": "N1", "topic": "T1", "from": ["ben-1"],
                                    "block": "owner", "predicted_useful": "extended"}])
check("предсказание «расширила» на трёх ступенях ловится",
      any("predicted_useful: extended" in p for p in ws.validate(three_pred)), True)

# The owner may rate on four ranks while the older text still asked on three; the
# record says so, and a three-rank prediction stays legal beside a four-rank mark.
moved = wave(charter_version="0.9.2", skill_version="0.9.3", useful_scale=4,
             findings=[{"id": "N1", "topic": "T1", "from": ["ben-1"], "block": "owner",
                        "predicted_useful": "refined", "useful": "extended",
                        "predicted": "fix", "ruling": "fix", "fix": "mine"}])
check("`useful_scale: 4` под старым скиллом законен", ws.validate(moved), [])
check("`useful_scale: 4` под старым скиллом — четыре ступени", moved.useful_scale, 4)
check("старый скилл без поля — три ступени", u.useful_scale, 3)
check("эпоха «правда ли» ступеней не знает", w.useful_scale, None)
for label, over, fragment in [
    ("ступеней пять", {**FOUR, "useful_scale": 5}, "useful_scale: 5"),
    ("три ступени под новым скиллом", {**FOUR, "useful_scale": 3}, "useful_scale: 3"),
    ("ступени в эпохе «правда ли»", {"useful_scale": 4}, "эпохи «правда ли»"),
]:
    check(f"неверный `useful_scale` ловится: {label}",
          any(fragment in p for p in ws.validate(wave(**over))), True)
check("ступени в строке волны", (ws.wave_stats(moved)["scale"], su["scale"], s["scale"]),
      (4, 3, None))


# ------------------------------------------------ time per run and per arm (0.11.0+)

# The lenses of an arm run in parallel, so an arm takes as long as its slowest run.
# Summing would triple it; a maximum over only the recorded runs would shrink it.
def timed(arm: str, lens: str, ms, tools) -> dict:
    r = {"id": f"{lens[:3]}-{arm}", "lens": lens, "arm": arm, "raw_findings": 1,
         "topics": [f"T{arm}{lens[:1]}"]}
    if ms is not None:
        r["duration_ms"] = ms
    if tools is not None:
        r["tool_uses"] = tools
    return r


tw = wave(effort="experimental", runs=[
    timed("A", "beneficiary", 780_000, 84), timed("A", "adversary", 912_000, 89),
    timed("A", "auditor", 1_086_000, 83),
    timed("B", "beneficiary", 600_000, 80), timed("B", "adversary", 660_000, 85),
    timed("B", "auditor", None, 82),
])
tarms = {r["arm"]: r for r in ws.arm_stats(tw)}
check("время руки — самый долгий прогон", tarms["A"]["minutes"], 18.1)
check("вызовы руки — сумма", tarms["A"]["tools"], 256)
check("прогон без времени гасит время руки", tarms["B"]["minutes"], None)
check("вызовы руки B при полной записи", tarms["B"]["tools"], 247)
check("время прогона в минутах", {r["run"]: r["minutes"] for r in ws.run_stats(tw)}["aud-A"], 18.1)
check("запись со временем проходит проверку", ws.validate(tw), [])
bad_time = wave(runs=[timed("A", "auditor", -5, "83")])
check("отрицательное время и строка вместо числа отвергнуты",
      len([p for p in ws.validate(bad_time) if "duration_ms" in p or "tool_uses" in p]), 2)
check("запись без времени — пусто, не ноль",
      {r["run"]: r["minutes"] for r in ws.run_stats(w)}["ben-1"], None)

# Grouped reading may change what a lens finds, so an arm that read in batches is
# its own series in the median -- even when it shares its topic pass with the
# plain arm, which is the whole design of that A/B.
def arm_run(arm: str, lens: str, topics: list[str], reads=None) -> dict:
    r = {"id": f"{lens[:3]}-{arm}", "lens": lens, "arm": arm,
         "raw_findings": len(topics), "topics": topics}
    if reads:
        r["reads"] = reads
    return r


rb = wave(effort="experimental", charter_version="0.11.0", skill_version="0.11.0",
          topic_pass={"model": "opus", "runs": 1, "topics": 40}, runs=[
    arm_run("A", "beneficiary", ["T1"]), arm_run("A", "adversary", ["T2", "T3"]),
    arm_run("A", "auditor", ["T4"]),
    arm_run("B", "beneficiary", ["T1", "T5"], "batch"),
    arm_run("B", "adversary", ["T3"], "batch"), arm_run("B", "auditor", ["T6"], "batch"),
])
check("запись с пакетной рукой проходит проверку", ws.validate(rb), [])
med = {(r["reads"], r["lens"]): r for r in ws.median_unique([rb])["rows"]}
check("обычная рука — свой ряд, уникальность внутри руки",
      (med[("по одному", "adversary")]["values"], med[("по одному", "adversary")]["sources"]),
      ([2], ["W99/A"]))
check("пакетная рука — свой ряд",
      (med[("пакетом", "beneficiary")]["values"], med[("пакетом", "beneficiary")]["sources"]),
      ([2], ["W99/B"]))
check("неизвестный режим чтения отвергнут",
      len([p for p in ws.validate(wave(runs=[arm_run("A", "auditor", ["T1"], "fast")]))
           if "reads" in p]), 1)

# From skill 0.16.0 every lens of a normal or enhanced wave reads in batches. A
# run there without the field is a record that forgot it, and the median would
# file it under the one-call-per-turn series without a word.
def default_reads(effort: str, skill: str, reads) -> ws.Wave:
    return wave(effort=effort, charter_version="0.12.0", skill_version=skill, runs=[
        arm_run("A", "beneficiary", ["T1"], "batch"),
        arm_run("A", "adversary", ["T2"], reads),
        arm_run("A", "auditor", ["T3"], "batch"),
    ])


def reads_problems(w: ws.Wave) -> list[str]:
    return [p for p in ws.validate(w) if "reads" in p]


check("обычная волна 0.16.0 без `reads` у прогона — отказ",
      len(reads_problems(default_reads("normal", "0.16.0", None))), 1)
check("усиленная волна 0.16.0 без `reads` у прогона — отказ",
      len(reads_problems(default_reads("enhanced", "0.16.0", None))), 1)
check("обычная волна 0.16.0, все прогоны пачками — проходит",
      ws.validate(default_reads("normal", "0.16.0", "batch")), [])
check("рука experimental читает по одному на 0.16.0 — проходит",
      reads_problems(default_reads("experimental", "0.16.0", None)), [])
check("обычная волна скилла 0.15.0 без `reads` — проходит, как записана",
      reads_problems(default_reads("normal", "0.15.0", None)), [])


# ------------------------------------------ a finding with two topics (0.13.0+)

# A lens that returned one finding carrying two topics used to be recorded by
# splitting its raw count, which put a number in the record the lens never returned.
two = wave(runs=[
    {"id": "aud-1", "lens": "auditor", "raw_findings": 1, "topics": ["T1", "T2"]},
])
check("две темы у одной находки без extra_topics — отказ",
      len([p for p in ws.validate(two) if "extra_topics" in p]), 1)
two_ok = wave(runs=[
    {"id": "aud-1", "lens": "auditor", "raw_findings": 1, "extra_topics": 1,
     "topics": ["T1", "T2"]},
])
check("две темы у одной находки с extra_topics: 1 — проходит", ws.validate(two_ok), [])
check("сырые остаются тем, что вернула линза", ws.wave_stats(two_ok)["raw_total"], 1)
check("отрицательные лишние темы отвергнуты",
      len([p for p in ws.validate(wave(runs=[
          {"id": "aud-1", "lens": "auditor", "raw_findings": 3, "extra_topics": -1,
           "topics": ["T1"]}])) if "extra_topics" in p]), 1)


# -------------------------------------------- the lens text splits the median

# 0.7.0 and 0.8.0 moved the skill and the tool, not what the lenses read; 0.9.2
# changed the charter's opening. So the first two share a series, the third does not.
def uncapped_at(version: str, wid: str) -> ws.Wave:
    return wave(wave=wid, charter_version=version, skill_version=version,
                topic_pass={"model": "sonnet", "runs": 1, "topics": 20})


check("текст линз 0.7.0 — это 0.6.0", ws.lens_text("0.7.0"), "0.6.0")
check("текст линз 0.9.3 — это 0.9.2", ws.lens_text("0.9.3"), "0.9.2")
check("текст линз 0.12.0", ws.lens_text("0.12.0"), "0.12.0")
series = {(r["lens_text"], r["lens"]): r["sources"]
          for r in ws.median_unique([uncapped_at("0.7.0", "W50"), uncapped_at("0.8.0", "W51"),
                                     uncapped_at("0.9.2", "W52")])["rows"]}
check("0.7.0 и 0.8.0 — один ряд", series[("0.6.0", "adversary")], ["W50", "W51"])
check("0.9.2 — свой ряд", series[("0.9.2", "adversary")], ["W52"])


# ----------------------------------- set aside vs refuted, main thread, author

sa = wave(charter_version="0.12.0", skill_version="0.12.0", authored_in_session=True,
          main_thread={"tokens": 410000, "duration_ms": 3_600_000},
          findings=[
    {"id": "F1", "topic": "T1", "from": ["ben-1"], "status": "removed",
     "removed_reason": "outside the delivery — later delivery"},
    {"id": "F2", "topic": "T3", "from": ["adv-1"], "status": "removed",
     "removed_reason": "ran the refutation: the guard is at db.py:212"},
    {"id": "F3", "topic": "T4", "from": ["aud-1"], "status": "shown", "block": "agent",
     "correction": "accepted"},
])
check("запись с отложенным, автором и главным потоком проходит", ws.validate(sa), [])
s_sa = ws.wave_stats(sa)
check("снято всего", s_sa["removed"], 2)
check("из них опровергнуто", s_sa["refuted"], 1)
check("из них отложено вне поставки", s_sa["set_aside"], 1)
check("токены главного потока", s_sa["mt_tokens"], 410000)
check("минуты главного потока", s_sa["mt_minutes"], 60.0)
check("объект писала эта сессия", s_sa["authored"], True)
check("догадка вместо числа у главного потока отвергнута",
      len([p for p in ws.validate(wave(main_thread={"tokens": "около 400k"}))
           if "main_thread" in p]), 1)
check("authored_in_session — только да или нет",
      len([p for p in ws.validate(wave(authored_in_session="yes"))
           if "authored_in_session" in p]), 1)


# ------------------------------------------------------------------ reach

check("охват: русская форма", ws.parse_reach("9 из 1 314 игр"), ("count", 9, 1314))
check("охват: английская форма", ws.parse_reach("12 of 1 400 items (0.9%)"), ("count", 12, 1400))
check("охват: весь объект", ws.parse_reach("весь объект")[0], "whole")
check("охват: не посчитан", ws.parse_reach("not counted — needs the live base")[0], "uncounted")
check("охват: мусор не разбирается", ws.parse_reach("примерно немного"), None)
check("корзина < 1%", ws.reach_bucket("9 из 1 314 игр"), "< 1%")
check("корзина ≥ 10%", ws.reach_bucket("247 из 305 игр"), "≥ 10%")
check("корзина без записи", ws.reach_bucket(None), "не записан")


def rated(fid: str, reach, useful: str) -> dict:
    f = {"id": fid, "topic": "T1", "from": ["ben-1"], "status": "shown", "block": "owner",
         "useful": useful, "predicted_useful": "refined", "predicted": "fix",
         "ruling": "no_fix", "fix": "none"}
    if reach is not None:
        f["reach"] = reach
    return f


rw = wave(charter_version="0.12.0", skill_version="0.12.0", findings=[
    rated("N1", "9 из 1 314 игр", "noise"),
    rated("N2", "весь объект", "changed"),
    rated("N3", None, "refined"),
])
check("запись с охватом проходит", ws.validate(rw), [])
rows = {r["bucket"]: r for r in ws.reach_marks([rw])["rows"]}
check("узкая находка — шум", (rows["< 1%"]["rated"], rows["< 1%"]["noise"]), (1, 1))
check("весь объект — изменила", rows["весь объект"]["changed"], 1)
check("без охвата — в «не записан»", rows["не записан"]["rated"], 1)
check("неразборчивый охват отвергнут",
      len([p for p in ws.validate(wave(charter_version="0.12.0", skill_version="0.12.0",
                                       findings=[rated("N1", "немного", "noise")]))
           if "reach" in p]), 1)
check("задето больше, чем всего, — отвергнуто",
      len([p for p in ws.validate(wave(charter_version="0.12.0", skill_version="0.12.0",
                                       findings=[rated("N1", "20 из 10", "noise")]))
           if "reach" in p]), 1)


# ------------------------------- body and appendix of the main thread's block (0.14.0+)

def agent_row(fid: str, topic: str, placed=None, correction=None) -> dict:
    f = {"id": fid, "topic": topic, "from": ["adv-1"], "status": "shown", "block": "agent"}
    if placed:
        f["placed"] = placed
    if correction:
        f["correction"] = correction
    return f


pl = wave(charter_version="0.14.0", skill_version="0.14.0", findings=[
    agent_row("N1", "T2", correction="accepted"),
    agent_row("N2", "T3", correction="amended"),
    agent_row("N3", "T2", placed="appendix"),
    agent_row("N4", "T3", placed="appendix"),
    agent_row("N5", "T2", placed="appendix", correction="overturned"),
])
check("запись с телом и приложением проходит", ws.validate(pl), [])
s_pl = ws.wave_stats(pl)
check("в теле — только строки тела", s_pl["body"], 2)
check("принято — только в теле", s_pl["corrections"]["accepted"], 1)
check("ответ по строкам тела", s_pl["answered_n"], "2/2")
check("в приложении строк", s_pl["appendix"], 3)
check("в приложении поправлено", s_pl["appendix_corrected"], 1)
check("в приложении не прочитано", s_pl["appendix_unread"], 2)
check("эпоха тела и приложения", s_pl["placement"], True)
check("молчание в приложении не согласие — accepted отвергнут",
      len([p for p in ws.validate(wave(charter_version="0.14.0", skill_version="0.14.0",
                                       findings=[agent_row("N1", "T2", "appendix", "accepted")]))
           if "приложени" in p]), 1)
check("placed у находки блока owner отвергнут",
      len([p for p in ws.validate(wave(charter_version="0.14.0", skill_version="0.14.0",
                                       findings=[{**rated("N1", None, "noise"), "placed": "body"}]))
           if "placed" in p]), 1)
check("до 0.14.0 — не эпоха тела и приложения",
      ws.wave_stats(wave(charter_version="0.10.1", skill_version="0.10.1"))["placement"], False)


# ------------------------- appendix rows he said he read (`appendix_read`, 0.17.0+)

# His words make an appendix row read; silence still does not. A row he said he
# read and did not correct is counted apart from the body's accepted and from
# the unread, and a corrected row stays corrected whatever he said of the rest.
SAID = {"where": "chat", "date": "2026-10-02", "quote": "Решения посмотрел, согласен"}


def placed_wave(said) -> ws.Wave:
    return wave(charter_version="0.14.0", skill_version="0.14.0", appendix_read=said, findings=[
        agent_row("N1", "T2", correction="accepted"),
        agent_row("N2", "T2", placed="appendix"),
        agent_row("N3", "T3", placed="appendix"),
        agent_row("N4", "T2", placed="appendix", correction="amended"),
    ])


def problems_about(said, needle="appendix_read") -> int:
    return len([p for p in ws.validate(placed_wave(said)) if needle in p])


all_read = placed_wave([{**SAID, "rows": "all"}])
check("высказывание обо всём приложении проходит", ws.validate(all_read), [])
s_all = ws.wave_stats(all_read)
check("по слову — все непоправленные строки приложения", s_all["appendix_read"], 2)
check("поправленная остаётся поправленной", s_all["appendix_corrected"], 1)
check("по слову — не непрочитанные", s_all["appendix_unread"], 0)
check("по слову — не принятые в теле", s_all["corrections"]["accepted"], 1)
check("его слова доходят до stats", s_all["appendix_said"][0]["quote"], SAID["quote"])

some_read = placed_wave([{**SAID, "rows": ["N2"]}])
check("высказывание о части строк проходит", ws.validate(some_read), [])
s_some = ws.wave_stats(some_read)
check("названная строка — по слову", s_some["appendix_read"], 1)
check("неназванная строка — не прочитана", s_some["appendix_unread"], 1)

silent = ws.wave_stats(placed_wave(None))
check("без высказывания молчание — не прочитано",
      (silent["appendix_read"], silent["appendix_unread"]), (0, 2))

check("без слов отвергнуто", problems_about([{"where": "chat", "rows": "all"}], "quote"), 1)
check("пустые слова отвергнуты", problems_about([{**SAID, "quote": "  ", "rows": "all"}], "quote"), 1)
check("неизвестное место отвергнуто", problems_about([{**SAID, "where": "call", "rows": "all"}]), 1)
check("неизвестный ключ отвергнут", problems_about([{**SAID, "rows": "all", "qoute": "x"}]), 1)
check("без rows отвергнуто", problems_about([SAID]), 1)
check("несуществующая строка отвергнута", problems_about([{**SAID, "rows": ["N9"]}]), 1)
check("строка тела отвергнута", problems_about([{**SAID, "rows": ["N1"]}]), 1)
check("поправленная строка отвергнута", problems_about([{**SAID, "rows": ["N4"]}]), 1)
check("не список отвергнут", problems_about({**SAID, "rows": "all"}), 1)
check("высказывание ни о чём отвергнуто",
      len([p for p in ws.validate(wave(charter_version="0.14.0", skill_version="0.14.0",
                                       appendix_read=[{**SAID, "rows": "all"}],
                                       findings=[agent_row("N1", "T2", correction="accepted")]))
           if "appendix_read" in p]), 1)
check("принятая по слову строка считается принятой у руки",
      ws._counts_as_accepted(all_read, next(f for f in all_read.findings if f.id == "N2")), True)
check("непрочитанная строка у руки не считается",
      ws._counts_as_accepted(some_read, next(f for f in some_read.findings if f.id == "N3")), False)


# ------------------------------------------------------------ the shipped template

# The template is the first record anyone copies. If it does not pass the check it
# ships a broken example, and if its era is wrong it teaches the old vocabulary.
import yaml  # noqa: E402

template_path = Path(__file__).resolve().parent.parent / "lab" / "wave_template.yaml"
template = ws.parse(yaml.safe_load(template_path.read_text(encoding="utf-8")), template_path)
check("шаблон записи волны проходит проверку", ws.validate(template), [])
check("шаблон записи волны — эпохи пользы", template.usefulness_era, True)
check("шаблон записи волны — четыре ступени пользы", template.useful_scale, 4)


# ----------------------------------------------------------------------- result

if FAILED:
    print(f"ПРОВАЛЕНО {len(FAILED)}:")
    for f in FAILED:
        print("  -", f)
    raise SystemExit(1)
print("все проверки пройдены")
