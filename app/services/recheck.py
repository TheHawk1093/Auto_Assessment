"""A second look at one answer, asked for from a regrade request.

The teacher can decide a request alone, or ask the pipeline to mark that one answer again with a
note saying what to look at, using this exam's model or another. The pipeline only proposes a
mark and feedback; the teacher reads the proposal and decides. Nothing here changes a mark.
"""

from __future__ import annotations

import json

from app.services import db, jobs, regrades


def proposal(exam_id: str, request_id: int) -> dict | None:
    """What the last recheck of this request proposed, or None."""
    path = jobs.recheck_path(exam_id, request_id)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def ask(exam_id: str, request_id: int, model_id: str, note: str, by: str) -> None:
    """Start the pipeline on the request's answer, with the teacher's note.

    Raises:
        ValueError: If the request is not waiting for a decision.
        RuntimeError: If another job is running or the model is unavailable.
    """
    row = next((r for r in regrades.list_requests(exam_id) if r["id"] == request_id), None)
    if row is None or row["status"] != "pending":
        raise ValueError("That request is not waiting for a decision.")
    # Only the teacher's note reaches the marker. The student's reason is data for the teacher to
    # weigh; it never goes to the model, where it could be written to steer the mark.
    jobs.start_recheck(exam_id, request_id, model_id, row["student"], row["question"], note.strip())
    db.audit(by, "recheck_asked", f"{exam_id} #{request_id} with {model_id}")


def running_for(exam_id: str) -> int | None:
    """The request id whose recheck is running in this exam, if any."""
    state = jobs.job_state(exam_id)
    if state.get("kind") == "recheck" and state.get("state") == "running":
        return state.get("request_id")
    return None
