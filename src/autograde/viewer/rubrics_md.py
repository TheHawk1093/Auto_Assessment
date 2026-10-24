"""Write stored rubrics as plain markdown, one file per dataset and strictness, for reading."""

from __future__ import annotations

from pathlib import Path

from autograde.datasets.loaders import load_dataset
from autograde.pipeline.rubric import cached_record, rubric_path
from autograde.pipeline.run import to_question


def rubric_markdown(dataset: str, variant: str, sections: list[str]) -> str:
    head = f"# {dataset}: {variant} rubrics\n\nMarks per point add up to the question total.\n"
    return head + "\n".join(sections)


def export_markdown(
    dataset: str, variant: str, client_name: str, data_dir: Path, rubrics_dir: Path
) -> Path | None:
    """Write `<rubrics_dir>/<client>/<variant>/<dataset>.md`. None if no rubric is stored."""
    questions = {}
    for item in load_dataset(dataset, data_dir):
        questions.setdefault(item.question_key, to_question(item))
    sections = []
    for key in sorted(questions):
        record = cached_record(rubrics_dir, client_name, key, variant)
        if record is None:
            continue
        q, rubric = questions[key], record.rubric
        points = "\n".join(
            f"- **{p.id}** ({p.marks:g}): {p.description}"
            + (f" _Partial: {p.partial_credit}_" if p.partial_credit else "")
            for p in rubric.points
        )
        stance = f"\n_{rubric.stance()}_\n" if rubric.stance() else ""
        sections.append(
            f"\n## {key} ({q.max_mark:g} marks)\n\n**Question:** {q.text}\n\n"
            f"**Model answer:** {q.model_answer}\n{stance}\n{points}\n"
        )
    if not sections:
        return None
    out = rubric_path(rubrics_dir, client_name, "x", variant).parent / f"{dataset}.md"
    out.write_text(rubric_markdown(dataset, variant, sections), encoding="utf-8")
    return out
