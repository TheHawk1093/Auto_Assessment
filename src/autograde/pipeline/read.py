"""Stage 3a: read the student's answer on its own, before it is marked."""

from __future__ import annotations

from autograde import prompts
from autograde.llm import LLMClient
from autograde.schemas import Item, Reading


def read_answer(item: Item, client: LLMClient) -> Reading | None:
    """Summarise what the student says. Sees only the question and the answer, never the model
    answer or the scheme, so the reading cannot be pulled towards the reference wording."""
    if not item.student_answer.strip():
        return None
    user = prompts.render("read.user", question=item.question, student_answer=item.student_answer)
    return client.ask(prompts.system("read"), user, Reading)


def reading_block(reading: Reading) -> str:
    """The reading as text to place in the marking prompt."""

    def bullets(xs: list[str]) -> str:
        return "\n".join(f"- {x}" for x in xs) if xs else "- none"

    return prompts.render(
        "reading.block",
        gist=reading.gist,
        ideas=bullets(reading.ideas),
        problems=bullets(reading.problems),
    )
