import zipfile

from autograde.intake.answers import load_answers
from autograde.intake.exam import build_items
from autograde.intake.figures import anchor_figures, split_figures
from autograde.intake.files import read_document
from autograde.intake.models import Paper, QuestionSpec, Reference

PNG = b"\x89PNG\r\n\x1a\n"


def paper():
    return Paper(
        questions=[
            QuestionSpec(id="1", text="State Ohm's law.", max_mark=2),
            QuestionSpec(id="2", text="Draw the circuit of a half-wave rectifier.", max_mark=4),
        ]
    )


def test_relative_images_become_absolute_and_split_from_the_words(tmp_path):
    (tmp_path / "d.png").write_bytes(PNG)
    text = anchor_figures("Here it is\n![my circuit](d.png)\nthat is all", tmp_path)
    words, figs = split_figures(text)
    assert figs == [(tmp_path / "d.png").resolve().as_posix()]
    assert "![" not in words and "that is all" in words


def test_a_figure_tag_and_a_missing_file(tmp_path):
    (tmp_path / "a.jpg").write_bytes(PNG)
    text = anchor_figures("[figure: a.jpg]\n[figure: gone.png]", tmp_path)
    _, figs = split_figures(text)
    assert figs[0].endswith("/a.jpg") and figs[1] == "gone.png"


def test_non_images_and_urls_are_not_figures(tmp_path):
    words, figs = split_figures("see ![x](notes.txt) and [figure: http://a/b.png]")
    assert figs == ["http://a/b.png"] or figs == []
    assert "notes.txt" not in " ".join(figs)


def test_answer_files_carry_their_drawings_into_the_items(tmp_path):
    (tmp_path / "ra.png").write_bytes(PNG)
    (tmp_path / "ans").mkdir()
    (tmp_path / "ans" / "sam.md").write_text("1. V = I R\n\n2. ![](../ra.png)\n", encoding="utf-8")
    answers, _ = load_answers(tmp_path / "ans", paper())
    refs = {"2": Reference(model_answer="A diode in series.\n![](ref.png)")}
    items = build_items("k", paper(), refs, answers)
    first, second = items
    assert first.figures == [] and first.student_answer == "V = I R"
    assert second.figures == [(tmp_path / "ra.png").resolve().as_posix()]
    assert second.kind == "diagram" and "drawing" in second.student_answer
    assert second.reference_figure == "ref.png" and second.model_answer == "A diode in series."


def test_docx_pictures_are_saved_and_referenced(tmp_path):
    doc = tmp_path / "sam.docx"
    body = (
        '<w:document xmlns:w="w" xmlns:r="r"><w:body>'
        "<w:p><w:r><w:t>2. My circuit:</w:t></w:r></w:p>"
        '<w:p><w:r><w:drawing><a:blip r:embed="rId5"/></w:drawing></w:r></w:p>'
        "</w:body></w:document>"
    )
    rels = (
        '<Relationships><Relationship Id="rId5" Type="image" Target="media/image1.png"/>'
        "</Relationships>"
    )
    with zipfile.ZipFile(doc, "w") as zf:
        zf.writestr("word/document.xml", body)
        zf.writestr("word/_rels/document.xml.rels", rels)
        zf.writestr("word/media/image1.png", PNG)
    words, figs = split_figures(read_document(doc))
    assert "My circuit" in words and len(figs) == 1
    assert (tmp_path / "sam_media" / "image1.png").read_bytes() == PNG
