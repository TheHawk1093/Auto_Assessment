"""Free what-if for the cascade: pair a cheap run with a strong run on the same answers."""

from __future__ import annotations

from itertools import combinations

from autograde.pipeline.cascade import TRIGGERS, unsure_because
from autograde.schemas import Result


def cascade_report(cheap: list[Result], strong: list[Result]) -> list[dict]:
    """Score each trigger set for escalating cheap marks to the strong model.

    For each trigger set: the share of answers re-marked and the error if the strong mark
    replaced the cheap one on exactly those answers. Error is a share of the total marks.
    """
    strong_by_id = {r.item.id: r for r in strong}
    pairs = [(c, strong_by_id[c.item.id]) for c in cheap if c.item.id in strong_by_id]
    pairs = [(c, s) for c, s in pairs if c.item.human_mark is not None and c.grading]
    if not pairs:
        return []
    sets = [()] + [c for n in (1, 2, 3, 4) for c in combinations(TRIGGERS, n)]
    rows = []
    for trig in sets:
        err, esc = 0.0, 0
        for c, s in pairs:
            hit = bool(trig) and unsure_because(c.grading, c.flags, c.item.max_mark, trig)
            esc += bool(hit)
            used = s if hit else c
            err += abs(used.predicted_mark - c.item.human_mark) / c.item.max_mark
        rows.append(
            {
                "triggers": "+".join(trig) or "none",
                "re_marked": round(esc / len(pairs), 2),
                "error": round(err / len(pairs), 3),
            }
        )
    everything = sum(
        abs(s.predicted_mark - c.item.human_mark) / c.item.max_mark for c, s in pairs
    ) / len(pairs)
    rows.append({"triggers": "all (strong alone)", "re_marked": 1.0, "error": round(everything, 3)})
    return rows
