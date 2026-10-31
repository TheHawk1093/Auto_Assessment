from pathlib import Path

import pandas as pd
import pytest

from autograde.datasets import load_dataset, select, split_of
from autograde.datasets.loaders import BENCHMARK_ONLY, LOADERS
from autograde.datasets.translate import BASES

SAF_XML = """<?xml version='1.0' encoding='utf-8'?>
<question id="10.1" module="TC">
  <questionText>State two differences between UDP and TCP.</questionText>
  <referenceAnswers><referenceAnswer id="a1">UDP is smaller.
TCP has sequence numbers.</referenceAnswer></referenceAnswers>
  <studentAnswers>
    <studentAnswer id="TC_10.1.1"><response>No submission.</response>
      <response_feedback>The response is empty.</response_feedback><score> 0</score></studentAnswer>
    <studentAnswer id="TC_10.1.2"><response>TCP has sequence numbers.</response>
      <response_feedback>Names one difference.</response_feedback><score>0.5</score></studentAnswer>
  </studentAnswers>
</question>"""


def test_saf(tmp_path: Path):
    d = tmp_path / "saf" / "data" / "training" / "english"
    d.mkdir(parents=True)
    (d / "10.1_TC.xml").write_text(SAF_XML, encoding="utf-8")
    items = load_dataset("saf", tmp_path)
    assert [i.human_mark for i in items] == [0.0, 0.5]
    assert items[1].question_id == "TC_10.1" and items[1].max_mark == 1.0
    assert items[0].model_answer == "UDP is smaller. TCP has sequence numbers."
    assert items[1].human_feedback == "Names one difference."


def test_digiklausur(tmp_path: Path):
    d = tmp_path / "digiklausur"
    d.mkdir()
    pd.DataFrame(
        {"question_id": [1, 1], "question": [" What is a neuron? ", " What is a neuron? "],
         "student_answer": ["A cell.", "A unit that sums inputs."],
         "ref_answer": ["A unit that sums inputs.", "A unit that sums inputs."],
         "grades_round": [0, 2]}
    ).to_csv(d / "asag_dataset.csv")  # fmt: skip
    items = load_dataset("digiklausur", tmp_path)
    assert [i.human_mark for i in items] == [0.0, 2.0]
    assert items[0].question == "What is a neuron?" and items[0].max_mark == 2.0


def test_mohler_strips_markers_and_groups_by_question(tmp_path: Path):
    d = tmp_path / "mohler"
    d.mkdir()
    pd.DataFrame(
        {"id": ["E01.Q01.A00", "E01.Q01.A01"], "question": ["Why? <STOP>"] * 2,
         "instructor_answer": ["Because. <STOP>"] * 2,
         "student_answer": ["Cause. <STOP> Yes. <STOP>", "No."],
         "score_grader_1": [4.0, 0.0], "score_grader_2": [5.0, 0.0], "score_avg": [4.5, 0.0]}
    ).to_parquet(d / "cleaned-oe-00001.parquet")  # fmt: skip
    items = load_dataset("mohler", tmp_path)
    assert {i.question_id for i in items} == {"E01.Q01"}
    assert items[0].student_answer == "Cause. Yes." and items[0].human_mark == 4.5


def test_split_is_deterministic_and_by_question():
    assert split_of("saf/TC_10.1") == split_of("saf/TC_10.1")
    keys = [f"mohler/E{i:02d}.Q01" for i in range(40)]
    assert {split_of(k) for k in keys} == {"dev", "test"}


def test_unknown_dataset():
    with pytest.raises(KeyError):
        load_dataset("nope", Path("."))


@pytest.mark.skipif(not Path("data/raw/saf").exists(), reason="datasets not downloaded")
@pytest.mark.parametrize("name", sorted(LOADERS))
def test_real_data_loads_and_samples(name: str):
    try:
        items = load_dataset(name, Path("data/raw"))
    except FileNotFoundError:
        pytest.skip(f"{name} is not downloaded (some sets are given on request only)")
    if name.split("_")[0] in BASES and name not in {"mohler", "digiklausur"} and not items:
        pytest.skip("translated set not built yet")
    assert len(items) > (20 if name == "circuit_hw" or name in BENCHMARK_ONLY - {"engsaf"} else 100)
    assert all(i.human_mark is not None for i in items)
    assert all(0 <= i.human_mark <= i.max_mark for i in items)
    sample = select(items, "dev", 10, seed=1)
    assert sample == select(items, "dev", 10, seed=1)
    if name not in BENCHMARK_ONLY:  # benchmark-only datasets ignore the split on purpose
        assert {split_of(i.question_key) for i in sample} == {"dev"}


def test_engsaf_loader_and_benchmark_only(tmp_path):
    import pandas as pd

    from autograde.datasets.loaders import load_engsaf, select

    folder = tmp_path / "engsaf"
    folder.mkdir()
    row = {"question": "Q?", "student_answer": "A", "reference_answer": "R", "score": 2}
    for part in ("train", "validation", "test"):
        pd.DataFrame([row, {**row, "student_answer": None, "score": 0}]).to_csv(
            folder / f"{part}.csv", index=False
        )
    items = load_engsaf(tmp_path)
    assert len(items) == 6 and items[0].max_mark == 2.0
    assert items[1].student_answer == ""
    # benchmark-only: every question is available whatever the dev/test split says
    assert len(select(items, "dev", None)) == len(select(items, "test", None)) == 6
