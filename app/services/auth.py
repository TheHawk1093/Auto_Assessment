"""Accounts: hashed passwords, roles, and the checks the pages rely on.

Passwords are stored as scrypt hashes (standard library), never in clear. Usernames are NFC
normalised; a student's username is the student id used in the answer files, which is what
links the account to that student's results.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets

from app.services import db, students
from app.text import normalize

ROLES = ("admin", "teacher", "student")
MIN_PASSWORD = 8
_ALPHABET = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no look-alike characters


def hash_password(password: str) -> str:
    """Return a salted scrypt hash of the password as `scrypt$salt$digest`."""
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt${salt.hex()}${digest.hex()}"


def check_password(password: str, stored: str) -> bool:
    """Say whether the password matches a hash made by `hash_password`."""
    try:
        _, salt, digest = stored.split("$")
        got = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=2**14, r=8, p=1)
    except ValueError:
        return False
    return hmac.compare_digest(got.hex(), digest)


def generate_password(length: int = 10) -> str:
    """Make a random password from characters that are hard to confuse."""
    return "".join(secrets.choice(_ALPHABET) for _ in range(length))


def has_users() -> bool:
    """Say whether any account exists yet (false on a fresh install)."""
    with db.connect() as c:
        return c.execute("SELECT 1 FROM users LIMIT 1").fetchone() is not None


def create_user(
    username: str,
    role: str,
    name: str,
    password: str,
    by: str = "system",
    allow_short: bool = False,
    student_id: str | None = None,
) -> None:
    """Add an account.

    A student account links to a student id (default: the username), which must not already
    have an account. `allow_short` skips the length rule; only the demo seeder uses it.

    Raises:
        ValueError: If the role is unknown, the username is empty or taken, the password is too
            short, or the student already has an account.
    """
    username = normalize(username).strip()
    if role not in ROLES:
        raise ValueError(f"Unknown role {role!r}.")
    if not username:
        raise ValueError("A username is required.")
    if len(password) < MIN_PASSWORD and not allow_short:
        raise ValueError(f"The password needs at least {MIN_PASSWORD} characters.")
    sid = None
    if role == "student":
        sid = students.ensure(student_id or username, name)
        if students.account_of(sid):
            raise ValueError(f"Student {sid!r} already has an account.")
    with db.connect() as c:
        if c.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone():
            raise ValueError(f"The username {username!r} is already taken.")
        c.execute(
            "INSERT INTO users (username, role, name, pw_hash, created, student_id)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (username, role, normalize(name).strip(), hash_password(password), db.now(), sid),
        )
    db.audit(by, "create_user", f"{username} ({role})")


def authenticate(username: str, password: str) -> dict | None:
    """Return the user if the password is right and the account is active.

    Returns:
        {username, role, name, student_id}, or None. `student_id` is None except for students.
    """
    username = normalize(username).strip()
    with db.connect() as c:
        row = c.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if row is None:
        hash_password(password)  # spend the same time whether or not the user exists
        return None
    if not row["active"] or not check_password(password, row["pw_hash"]):
        return None
    return {
        "username": row["username"],
        "role": row["role"],
        "name": row["name"],
        "student_id": row["student_id"],
    }


def set_password(username: str, password: str, by: str, allow_short: bool = False) -> None:
    """Change an account's password.

    Raises:
        ValueError: If the password is shorter than `MIN_PASSWORD` and `allow_short` is false.
    """
    if len(password) < MIN_PASSWORD and not allow_short:
        raise ValueError(f"The password needs at least {MIN_PASSWORD} characters.")
    with db.connect() as c:
        c.execute(
            "UPDATE users SET pw_hash = ? WHERE username = ?", (hash_password(password), username)
        )
    db.audit(by, "set_password", username)


def set_name(username: str, name: str, by: str) -> None:
    """Change the name an account is shown under. The username never changes.

    For a student account the student's own record is changed too, so the two cannot differ.
    """
    name = normalize(name).strip()
    with db.connect() as c:
        row = c.execute("SELECT student_id FROM users WHERE username = ?", (username,)).fetchone()
        if row is None:
            raise ValueError(f"There is no account {username!r}.")
        c.execute("UPDATE users SET name = ? WHERE username = ?", (name, username))
        if row["student_id"]:
            c.execute(
                "UPDATE students SET name = ? WHERE student_id = ?", (name, row["student_id"])
            )
    db.audit(by, "set_name", username)


def set_active(username: str, active: bool, by: str) -> None:
    """Enable or disable an account."""
    with db.connect() as c:
        c.execute("UPDATE users SET active = ? WHERE username = ?", (int(active), username))
    db.audit(by, "enable_user" if active else "disable_user", username)


def list_users(role: str | None = None) -> list[dict]:
    """List accounts (optionally of one role), ordered by role and username."""
    with db.connect() as c:
        sql = "SELECT username, role, name, student_id, active, created FROM users"
        rows = c.execute(sql + (" WHERE role = ?" if role else "") + " ORDER BY role, username",
                         (role,) if role else ()).fetchall()  # fmt: skip
    return [dict(r) for r in rows]


def exists(username: str) -> bool:
    """Say whether a username is taken."""
    with db.connect() as c:
        return (
            c.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone() is not None
        )
