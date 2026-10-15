import json
import re
from pathlib import Path

from autograde.schemas import Feedback, Grading, Improvement, Item, PointVerdict, Result
from autograde.viewer.build import build_data, render_html


def make_result() -> Result:
    item = Item(id="t/1", dataset="t", question_id="q", question="Why </script> matters?",
                model_answer="m", student_answer="It updates weights.", max_mark=2.0,
                human_mark=1.0)  # fmt: skip
    verdict = PointVerdict(point_id="P1", status="met", marks_awarded=1.0,
                           evidence="updates weights", reason="r")  # fmt: skip
    return Result(
        item=item,
        mode="pipeline",
        predicted_mark=1.0,
        grading=Grading(verdicts=[verdict]),
        feedback=Feedback(strengths=["ok"], improvements=[Improvement(point_id="P1", issue="i",
                                                                     fix="f")], summary="s"),
    )  # fmt: skip


def test_page_embeds_data_and_cannot_be_broken_by_answer_text(tmp_path: Path):
    data = build_data([make_result()], "demo", tmp_path, "fake")
    html = render_html(data)
    assert "__DATA__" not in html
    block = re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S)
    parsed = json.loads(block.group(1))  # raises if the embedded JSON broke out of the tag
    assert parsed["items"][0]["item"]["question"] == "Why </script> matters?"
    assert parsed["metrics"]["overall"]["n"] == 1
    assert parsed["items"][0]["points"] == {}  # no cached scheme, page still builds


def test_sample_spread_covers_questions_before_repeating():
    from autograde.viewer import sample_spread

    def res(q: str, i: int) -> Result:
        r = make_result()
        r.item = r.item.model_copy(update={"id": f"{q}/{i}", "question_id": q})
        return r

    pool = [res(q, i) for q in "abc" for i in range(4)]
    picked = sample_spread(pool, 3, seed=1)
    assert {r.item.question_id for r in picked} == {"a", "b", "c"}
    assert len(sample_spread(pool, 100)) == 12
