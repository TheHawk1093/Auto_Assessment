"""The offline mock backend: it must build from config and drive the real pipeline."""

import csv
import shutil
from pathlib import Path

import yaml
from pydantic import BaseModel

from autograde.cli import main
from autograde.config import LLMConfig, load_settings
from autograde.llm import build_client, client_name
from autograde.llm.mock import MockClient
from autograde.schemas import Feedback, Grading, RubricDraft

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / "examples" / "exam_demo"
MODEL_ANSWER = "Gradient descent updates the weights. It moves against the gradient."


def _rubric_prompt(total: float = 2.0) -> str:
    return f"Question:\nq\n\nModel answer:\n{MODEL_ANSWER}\n\nTotal marks: {total:g}\n"


def test_build_client_returns_the_mock_for_the_mock_backend():
    cfg = LLMConfig(backend="mock", model="offline")
    assert isinstance(build_client(cfg), MockClient)
    assert client_name(cfg) == "mock-offline"


def test_scheme_marks_add_up_to_the_total():
    draft = MockClient().ask("", _rubric_prompt(3.0), RubricDraft)
    assert abs(sum(p.marks for p in draft.points) - 3.0) < 1e-6
    assert len(draft.points) == 2  # one point per sentence of the model answer


def test_marker_awards_a_point_only_with_a_verbatim_quote():
    client = MockClient()
    scheme = client.ask("", _rubric_prompt(), RubricDraft).to_rubric()
    answer = "Gradient descent updates the weights."
    user = (
        f"Marking scheme:\n{scheme.render()}\n\n"
        f"Student answer:\n{answer}\n\nMark the student answer."
    )
    grading = client.ask("", user, Grading)
    by_id = {v.point_id: v for v in grading.verdicts}
    assert by_id["P1"].status == "met" and by_id["P1"].evidence in answer
    assert by_id["P2"].status == "not_met" and by_id["P2"].marks_awarded == 0


def test_feedback_names_each_missed_point():
    user = (
        'P1 [met, 1/1]: updates weights. Student wrote: "x". ok\n'
        "P2 [not_met, 0/1]: uses gradient. no"
    )
    fb = MockClient().ask("", user, Feedback)
    assert [i.point_id for i in fb.improvements] == ["P2"]
    assert fb.strengths


def test_unknown_schema_gets_a_valid_minimal_value():
    class Odd(BaseModel):
        name: str
        count: int
        tags: list[str]

    got = MockClient().ask("", "", Odd)
    assert got.name == "mock" and got.count == 0 and got.tags == []


def test_usage_is_counted():
    client = MockClient()
    client.ask("", _rubric_prompt(), RubricDraft)
    assert client.usage.calls == 1


def test_exam_command_runs_offline_end_to_end(tmp_path, monkeypatch):
    """`autograde exam` with configs/mock.yaml: schemes, marks, feedback, no key, no network."""
    cfg = yaml.safe_load((ROOT / "configs" / "mock.yaml").read_text(encoding="utf-8"))
    cfg["paths"] = {"data_dir": str(tmp_path / "data"), "rubrics_dir": str(tmp_path / "rubrics"),
                    "runs_dir": str(tmp_path / "runs")}  # fmt: skip
    config = tmp_path / "mock.yaml"
    config.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    answers = tmp_path / "answers"
    shutil.copytree(DEMO / "answers", answers)
    monkeypatch.chdir(tmp_path)  # the experiment log is written relative to the working directory

    main(["--config", str(config), "exam", "--paper", str(DEMO / "paper.json"),
          "--reference", str(DEMO / "reference_model_only.json"),
          "--answers", str(answers), "--name", "smoke"])  # fmt: skip

    run = tmp_path / "runs" / "smoke"
    rows = list(csv.DictReader((run / "marks.csv").open(encoding="utf-8")))
    assert {r["student"] for r in rows} == {"alice", "bob", "cara"}
    assert all(0 <= float(r["total"]) <= 12 for r in rows)
    assert (run / "schemes.md").read_text(encoding="utf-8").strip()
    # Feedback is mandatory for every answer that lost marks.
    assert "Question 1" in (run / "students" / "bob.md").read_text(encoding="utf-8")


def test_example_configs_load():
    for name in ("default", "exam", "mock", "poc"):
        assert load_settings(ROOT / "configs" / f"{name}.yaml") is not None
