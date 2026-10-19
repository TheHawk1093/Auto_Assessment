from autograde.evaluation.voting import vote_report
from autograde.pipeline.feedback import Pick, problems, write_feedback
from autograde.pipeline.vote import combine
from autograde.schemas import (
    Feedback,
    Grading,
    Improvement,
    Item,
    PointVerdict,
    Result,
    Rubric,
    RubricPoint,
)
from fakes import FakeClient

RUBRIC = Rubric(
    points=[
        RubricPoint(id="P1", description="a", marks=1.0),
        RubricPoint(id="P2", description="b", marks=1.0),
    ]
)


def grading(s1: str, s2: str) -> Grading:
    def v(pid: str, status: str) -> PointVerdict:
        return PointVerdict(point_id=pid, status=status, marks_awarded=0.0, evidence="", reason="r")

    return Grading(verdicts=[v("P1", s1), v("P2", s2)])


def test_majority_per_point_and_split_report():
    gs = [grading("met", "not_met"), grading("met", "met"), grading("partial", "not_met")]
    out, split = combine(gs, RUBRIC, "answer", partial_weight=0.9)
    assert [v.status for v in out.verdicts] == ["met", "not_met"]
    assert out.total == 1.0
    assert split == ["P1", "P2"]


def test_no_majority_takes_the_middle_verdict():
    gs = [grading("met", "met"), grading("partial", "met"), grading("not_met", "met")]
    out, split = combine(gs, RUBRIC, "answer", partial_weight=0.9)
    assert out.verdicts[0].status == "partial" and out.verdicts[0].marks_awarded == 0.9
    assert split == ["P1"]


def _item() -> Item:
    return Item(
        id="1", dataset="d", question_id="q", question="Q?", model_answer="the cat sat on the mat",
        student_answer="S", max_mark=2, human_mark=1,
    )  # fmt: skip


def _fb(why: str = "because") -> Feedback:
    return Feedback(
        strengths=[],
        improvements=[Improvement(point_id="P1", issue="i", why=why, fix="f")],
        summary="s",
    )


def test_problems_flags_missing_points_and_leaks():
    g = grading("not_met", "not_met").model_copy()
    assert "missing:P2" in problems(_fb(), _item(), g, RUBRIC, "standard")
    assert "no_why" in problems(_fb(why=""), _item(), g, RUBRIC, "standard")
    leaky = Feedback(strengths=["the cat sat on the mat"], improvements=[], summary="s")
    assert "gives_away_answer" in problems(leaky, _item(), g, RUBRIC, "standard")


def test_best_of_n_drafts_then_picks():
    g = grading("not_met", "met")
    client = FakeClient(
        {Feedback: lambda _u: _fb().model_dump(), Pick: lambda _u: {"choice": 2, "reason": "x"}}
    )
    write_feedback(_item(), RUBRIC, g, client, "standard", n=3)
    assert client.count(Feedback) == 3 and client.count(Pick) == 1


def test_vote_report_compares_single_and_voted():
    item = _item()
    rows = [
        Result(item=item, mode="pipeline", predicted_mark=1.0, votes=[0.0, 1.0, 1.0]),
        Result(item=item, mode="pipeline", predicted_mark=1.0, votes=[1.0, 1.0, 1.0]),
    ]
    rep = vote_report(rows)
    assert rep["n"] == 2 and rep["error_voted"] == 0.0
    assert rep["share_votes_all_agree"] == 0.5


def test_perturbations_keep_ids_and_change_question_key():
    from autograde.datasets.perturb import mask_words, parse, perturb_items, shorten

    text = "Gradient descent updates weights. It follows the negative gradient. Rates matter."
    assert shorten(text, 0.3).count(".") == 1
    masked = mask_words(text, 0.5, seed=1)
    assert "____" in masked and len(masked.split()) == len(text.split())
    assert parse("mask30") == ("mask", 0.3)
    item = Item(
        id="1", dataset="d", question_id="q", question="Q?", model_answer=text,
        student_answer="S", max_mark=2, human_mark=1,
    )  # fmt: skip
    out = perturb_items([item], "short50")[0]
    assert out.id == item.id and out.question_key != item.question_key


def test_stress_cases_and_expectations():
    from autograde.evaluation.stress import build_cases, passed, summarise

    items = [
        Item(
            id=f"{i}", dataset="d", question_id=f"q{i % 2}", question="Q?",
            model_answer="alpha beta gamma delta epsilon zeta", max_mark=2,
            student_answer="alpha beta gamma delta " * 3, human_mark=2.0 if i < 6 else 0.0,
        )
        for i in range(10)
    ]  # fmt: skip
    cases = build_cases(items, per_kind=2, seed=0)
    kinds = {c.kind for c in cases}
    assert {"paste_model", "shuffled", "keyword_list", "off_topic", "injection"} <= kinds
    paste = next(c for c in cases if c.kind == "paste_model")
    assert passed(paste, 2.0) and not passed(paste, 0.5)
    rows = [{"kind": "shuffled", "passed": True}, {"kind": "shuffled", "passed": False}]
    assert summarise(rows)["by_kind"]["shuffled"]["pass_rate"] == 0.5


def test_models_disagree_and_review_report():
    from autograde.evaluation.voting import review_report
    from autograde.pipeline.vote import models_disagree

    assert models_disagree(2.0, 1.0, 2.0, 0.15)
    assert not models_disagree(2.0, 1.9, 2.0, 0.15)
    item = Item(
        id="1", dataset="d", question_id="q", question="Q?", model_answer="M",
        student_answer="S", max_mark=2, human_mark=2,
    )  # fmt: skip
    ok = Result(item=item, mode="pipeline", predicted_mark=2.0, second_mark=2.0)
    bad = Result(
        item=item, mode="pipeline", predicted_mark=1.0, second_mark=2.0, flags=["models_disagree"]
    )
    rep = review_report([ok, bad])
    assert (
        rep["share_flagged"] == 0.5 and rep["error_when_flagged"] > rep["error_when_models_agree"]
    )


def test_form_gate_zeroes_incoherent_and_caps_keyword_lists():
    from autograde.pipeline.verify import apply_form_gate
    from autograde.schemas import Reading

    g = Grading(
        verdicts=[
            PointVerdict(point_id="P1", status="met", marks_awarded=1.0, evidence="x", reason="r"),
            PointVerdict(point_id="P2", status="met", marks_awarded=1.0, evidence="y", reason="r"),
        ]
    )

    def reading(form: str) -> Reading:
        return Reading(gist="g", ideas=[], problems=[], form=form)

    zero, flag = apply_form_gate(g, reading("incoherent"), 2.0)
    assert zero.total == 0.0 and flag == "incoherent_answer"
    cap, flag = apply_form_gate(g, reading("keyword_list"), 2.0)
    assert cap.total == 1.0 and flag == "keyword_list_capped"
    same, flag = apply_form_gate(g, reading("short_answer"), 2.0)
    assert same.total == 2.0 and flag is None
    assert apply_form_gate(g, None, 2.0) == (g, None)


def test_level_changes_policy_weight_and_prompt():
    from autograde.pipeline.levels import (
        LEVEL_PARTIAL_WEIGHT,
        LEVEL_POLICY,
        level_prompt,
    )
    from autograde.pipeline.rubric import rubric_prompt

    assert (
        LEVEL_PARTIAL_WEIGHT["lenient"]
        > LEVEL_PARTIAL_WEIGHT["moderate"]
        > LEVEL_PARTIAL_WEIGHT["harsh"]
    )
    assert set(LEVEL_POLICY) == {"lenient", "moderate", "harsh"}
    text = rubric_prompt("harsh", "saf")
    assert "HARSH" in text and "Computer-networks" in text  # level text plus the dataset policy
    assert "Neural-networks" in level_prompt("lenient", "digiklausur")
    assert "Computer-networks" not in level_prompt("lenient", "unknown")


def test_rubric_stance_is_shown_to_the_marker():
    rub = Rubric(
        points=[RubricPoint(id="P1", description="a", marks=1.0)],
        notes="Full marks for the core idea.",
        level="harsh",
    )
    assert rub.render().startswith("Marking stance: harsh. Full marks for the core idea.")
    assert Rubric(points=[RubricPoint(id="P1", description="a", marks=1.0)]).stance() == ""


def test_compliance_orders_levels():
    from autograde.evaluation.compliance import compliance

    def run(mark: float) -> list[Result]:
        item = Item(
            id="1", dataset="d", question_id="q", question="Q?", model_answer="M",
            student_answer="S", max_mark=2, human_mark=1,
        )  # fmt: skip
        return [Result(item=item, mode="pipeline", predicted_mark=mark)]

    out = compliance({"lenient": run(2.0), "moderate": run(1.5), "harsh": run(0.5)})
    assert out["ordering"]["share_strictly_falling"] == 1.0
    assert out["ordering"]["mean_lenient_minus_harsh"] == 0.75
