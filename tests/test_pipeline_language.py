from autograde.pipeline.feedback import _finish, full_marks_feedback
from autograde.schemas import Feedback, Grading, PointVerdict, Rubric, RubricPoint


def test_marathi_feedback_has_marathi_labels_and_no_english_opener():
    fb = Feedback(strengths=["x"], improvements=[], summary="Overall, तुम्ही छान लिहिले.")
    done = _finish(fb, "Marathi")
    assert done.summary == "तुम्ही छान लिहिले." and "Overall" not in done.text()
    assert "तुम्ही चांगले काय केले" in done.text()
    assert Feedback(strengths=["y"], improvements=[], summary="s").text().startswith("What you")


def test_full_marks_feedback_is_in_the_students_language():
    rubric = Rubric(points=[RubricPoint(id="P1", description="Idea.", marks=1)])
    graded = Grading(
        verdicts=[
            PointVerdict(point_id="P1", status="met", marks_awarded=1, evidence="e", reason="r")
        ]
    )
    fb = full_marks_feedback(rubric, graded, "Hindi")
    assert "पूरे अंक" in fb.summary and fb.language == "Hindi"


def test_every_language_table_has_the_same_labels():
    from autograde.localize import ENGLISH, STRINGS

    for language, table in STRINGS.items():
        assert table.keys() == ENGLISH.keys(), language


def test_language_note_is_only_for_other_languages():
    from autograde.pipeline.feedback import _system, language_note

    assert language_note("") == ""
    assert "in Tamil" in language_note("Tamil") and "நீங்கள்" in language_note("Tamil")
    assert "Tamil" not in _system("feedback", False)  # English prompts never see it
    assert "in Hindi" in _system("feedback", False, language="Hindi")
