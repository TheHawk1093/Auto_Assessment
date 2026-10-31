"""Drawings, graphs, circuits and other figures.

The marker is a text model and cannot see an image, so a vision model first describes the
student's drawing (and the model drawing, when there is one) as structured text: what is drawn,
the labels, how parts connect, the values written, and what could not be read. The marker then
judges the points about the drawing from that description. This is stated to the marker and
flagged for the teacher, because a description can miss a small error.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from autograde import prompts
from autograde.config import Settings
from autograde.llm import LLMError
from autograde.llm.openrouter import first_json_object
from autograde.ocr.hosted import PROVIDERS
from autograde.schemas import Item

# (images, system prompt, user text) -> the model's reply
Describer = Callable[[list[Path], str, str], str]


class FigureDescription(BaseModel):
    """A vision model's text description of a drawing; the marker never sees the image."""

    kind: str = Field(default="", description="circuit, graph, flowchart, free-body diagram, ...")
    elements: list[str] = Field(default_factory=list, description="What is drawn, one per item.")
    labels: list[str] = Field(default_factory=list, description="Text and symbols written on it.")
    connections: list[str] = Field(default_factory=list, description="How parts connect or relate.")
    values: list[str] = Field(default_factory=list, description="Numbers and units shown.")
    unclear: list[str] = Field(default_factory=list, description="Parts that could not be read.")
    legible: bool = True

    @field_validator("elements", "labels", "connections", "values", "unclear", mode="before")
    @classmethod
    def _as_text(cls, entries: object) -> object:
        """Models sometimes give each entry as a small object; keep it as readable text."""
        if not isinstance(entries, list):
            return entries
        return [
            "; ".join(f"{k}: {v}" for k, v in e.items()) if isinstance(e, dict) else str(e)
            for e in entries
        ]

    def render(self) -> str:
        """Format the description as text for the marker."""
        parts = [f"Kind: {self.kind or 'unknown'}"]
        for name, items in (
            ("Elements", self.elements),
            ("Labels", self.labels),
            ("Connections", self.connections),
            ("Values", self.values),
            ("Could not be read", self.unclear),
        ):
            if items:
                parts.append(f"{name}: " + "; ".join(items))
        if not self.legible:
            parts.append("The drawing is hard to read.")
        return "\n".join(parts)


def make_describer(settings: Settings) -> Describer:
    """A describer that uses the configured reader model (a hosted vision model)."""
    spec = settings.ocr.reader
    if spec.provider not in PROVIDERS:
        raise LLMError(f"{spec.provider!r} cannot describe figures; use a hosted vision reader")
    call = PROVIDERS[spec.provider]
    return lambda pages, system, user: call(pages, spec.model, system, user)


def describe_figure(paths: list[str], describer: Describer) -> FigureDescription:
    """Have the vision model describe the drawing on the given image pages."""
    pages = [Path(p) for p in paths]
    reply = describer(pages, prompts.system("figure.describe"), "Describe the drawing.")
    return FigureDescription.model_validate(first_json_object(reply))


def figure_notes(item: Item, describer: Describer | None) -> tuple[str, list[str]]:
    """Facts for the marker about the drawing, and flags for the teacher."""
    if not item.figures and item.kind != "diagram":
        return "", []
    if not item.figures:
        return "", ["figure_missing"]
    if describer is None:
        return (
            "The student drew a figure but no vision model is configured to read it. Do not give "
            "credit for points that need the drawing.",
            ["figure_not_checked"],
        )
    try:
        student = describe_figure(item.figures, describer)
        reference = (
            describe_figure([item.reference_figure], describer) if item.reference_figure else None
        )
    except (LLMError, ValueError, OSError) as exc:  # no reply, bad reply, unreadable file
        return (
            f"The drawing could not be read ({str(exc)[:80]}). Do not credit drawing points.",
            ["figure_not_checked"],
        )
    text = (
        "The student's drawing, described by a vision model (you cannot see the image; judge the "
        "drawing points from this description only):\n" + student.render()
    )
    if reference is not None:
        text += "\n\nThe model drawing, described the same way:\n" + reference.render()
    flags = ["figure_from_description"] + ([] if student.legible else ["figure_unclear"])
    return text, flags
