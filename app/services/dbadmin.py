"""What an administrator may change directly in the database, table by table.

Each table lists the columns that can be edited and whether rows can be deleted; keys, password
hashes and the audit log are never editable. Edits go through the same services the pages use
where one exists (a student's name also changes the account's name), every change is audited,
and `backup` copies the whole database first.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime

import pandas as pd

from app import config
from app.services import auth, courses, db, students

# table: (key columns, editable columns, rows may be deleted). Columns not listed are shown only.
TABLES: dict[str, tuple[list[str], list[str], bool]] = {
    "students": (["student_id"], ["name", "email"], True),
    "users": (["username"], ["role", "name", "active"], False),
    "courses": (["id"], ["title", "term", "teacher"], True),
    "enrolments": (["course_id", "student_id"], ["status"], True),
    "overrides": (["exam_id", "student", "question"], ["mark", "comment"], True),
    "regrades": (["id"], [], True),
    "submissions": (["exam_id", "student_id"], [], True),
    "notifications": (["id"], [], True),
    "audit": (["id"], [], False),
}
HIDDEN = {"users": ["pw_hash"]}
BACKUPS = config.APP_DATA / "backups"


def keys(table: str) -> list[str]:
    """The table's key columns."""
    return TABLES[table][0]


def editable(table: str) -> list[str]:
    """The columns an administrator may change."""
    return TABLES[table][1]


def deletable(table: str) -> bool:
    """Whether rows of the table may be deleted here."""
    return TABLES[table][2]


def rows(table: str) -> pd.DataFrame:
    """The table's rows (newest keys last), without secret columns."""
    with db.connect() as c:
        data = c.execute(f"SELECT * FROM {table}").fetchall()  # noqa: S608 - table is whitelisted
    frame = pd.DataFrame([dict(r) for r in data])
    return frame.drop(columns=HIDDEN.get(table, []), errors="ignore")


def _same(a, b) -> bool:
    return (pd.isna(a) and pd.isna(b)) or a == b


def apply(table: str, original: pd.DataFrame, edited: pd.DataFrame, by: str) -> tuple[int, int]:
    """Save the differences between the table as shown and as edited.

    `edited` may carry a boolean `delete` column. Rows are matched by position.

    Returns:
        (rows updated, rows deleted).

    Raises:
        ValueError: With a message to show, if the database refuses a change.
    """
    key_cols, edit_cols, can_delete = TABLES[table]
    updated = deleted = 0
    for (_, old), (_, new) in zip(original.iterrows(), edited.iterrows(), strict=True):
        where = [old[k] for k in key_cols]
        if can_delete and bool(new.get("delete", False)):
            _delete(table, key_cols, where)
            db.audit(by, "db_delete", f"{table} {where}")
            deleted += 1
            continue
        changes = {c: new[c] for c in edit_cols if not _same(old[c], new[c])}
        if changes:
            _update(table, key_cols, where, changes, old, by)
            updated += 1
    return updated, deleted


def _clean(value):
    return None if pd.isna(value) else (value.item() if hasattr(value, "item") else value)


def _update(table, key_cols, where, changes, old, by) -> None:
    where = [_clean(w) for w in where]
    changes = {c: _clean(v) for c, v in changes.items()}
    if table == "students":
        students.update(
            where[0],
            changes.get("name", old["name"]) or "",
            changes.get("email", old["email"]) or "",
            by,
        )
        return
    if table == "users" and set(changes) == {"name"}:
        auth.set_name(where[0], changes["name"] or "", by)
        return
    sets = ", ".join(f"{c} = ?" for c in changes)
    cond = " AND ".join(f"{k} = ?" for k in key_cols)
    try:
        with db.connect() as c:
            c.execute(f"UPDATE {table} SET {sets} WHERE {cond}", [*changes.values(), *where])  # noqa: S608
    except sqlite3.IntegrityError as e:
        raise ValueError(f"{table} {where}: the database refused that value ({e}).") from e
    db.audit(by, "db_update", f"{table} {where} {list(changes)}")


def _delete(table, key_cols, where) -> None:
    where = [_clean(w) for w in where]
    if table == "courses":
        courses.delete_course(int(where[0]), "admin")  # refuses while the course has exams
        return
    cond = " AND ".join(f"{k} = ?" for k in key_cols)
    try:
        with db.connect() as c:
            c.execute(f"DELETE FROM {table} WHERE {cond}", where)  # noqa: S608
    except sqlite3.IntegrityError as e:
        raise ValueError(
            f"{table} {where} is still used by other records; remove those first ({e})."
        ) from e


def backup(by: str) -> str:
    """Copy the database to app_data/backups and return the file name."""
    BACKUPS.mkdir(parents=True, exist_ok=True)
    target = BACKUPS / f"app-{datetime.now():%Y%m%d-%H%M%S}.db"
    src = sqlite3.connect(db.PATH)
    try:
        dst = sqlite3.connect(target)
        try:
            src.backup(dst)
        finally:
            dst.close()
    finally:
        src.close()
    db.audit(by, "db_backup", target.name)
    return target.name


def backups() -> list[str]:
    """Backup files, newest first."""
    return (
        sorted((p.name for p in BACKUPS.glob("app-*.db")), reverse=True) if BACKUPS.exists() else []
    )
