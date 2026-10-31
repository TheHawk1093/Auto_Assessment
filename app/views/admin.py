"""Admin page: accounts, which AI models teachers may use, and what is on the machine now."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.services import auth, courses, db, dbadmin, jobs, models, overview, storage, students
from app.ui import components as ui
from app.ui import session


def render() -> None:
    """Show the admin page: users, courses and students, AI models, exams and jobs."""
    ui.page_header("Admin", "Accounts, AI models and running jobs.")
    users_tab, people_tab, models_tab, exams_tab, data_tab = st.tabs(
        [
            ":material/group: Users",
            ":material/school: Courses and students",
            ":material/smart_toy: AI models",
            ":material/work: Exams and jobs",
            ":material/database: Database",
        ]
    )
    with users_tab:
        _users()
    with people_tab:
        _people()
    with models_tab:
        _models()
    with exams_tab:
        _exams()
    with data_tab:
        _database()


# ---------- users ----------


def _users() -> None:
    me = session.current_user()["username"]
    users = auth.list_users()
    st.dataframe(pd.DataFrame(users), hide_index=True, width="stretch")
    with st.expander("Add a teacher or admin"), st.form("add_user", clear_on_submit=True):
        username = st.text_input("Username")
        name = st.text_input("Name")
        role = st.selectbox("Role", ["teacher", "admin"])
        if st.form_submit_button("Create"):
            password = auth.generate_password()
            try:
                auth.create_user(username, role, name, password, by=me)
            except ValueError as e:
                st.error(str(e))
            else:
                st.session_state["issued"] = (username, password)
    issued = st.session_state.get("issued")
    if issued:
        st.warning(f"First password for **{issued[0]}**: `{issued[1]}`. It is shown only now.")
    _rename_user(users, me)
    names = [u["username"] for u in users if u["username"] != me]
    if not names:
        return
    with st.expander("Reset a password or disable an account"):
        who = st.selectbox("Account", names)
        c1, c2, _ = st.columns(3)
        if c1.button("Reset password"):
            password = auth.generate_password()
            auth.set_password(who, password, by=me)
            st.session_state["issued"] = (who, password)
            st.rerun()
        active = next(u["active"] for u in users if u["username"] == who)
        if c2.button("Disable" if active else "Enable"):
            auth.set_active(who, not active, by=me)
            st.rerun()


# ---------- courses and students ----------


def _people() -> None:
    """Every course with its teacher and head-count, and every student with their account."""
    rows = [
        {
            "course": courses.label(c),
            "teacher": c["teacher_name"] or c["teacher"],
            "term": c["term"],
            "enrolled": len(courses.roster(c["id"])),
        }
        for c in courses.list_courses()
    ]
    me = session.current_user()["username"]
    st.subheader("Courses")
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    _edit_course(me)
    st.subheader("Students")
    everyone = students.all_students()
    for s in everyone:
        s["courses"] = ", ".join(courses.label(c) for c in courses.courses_of(s["student_id"]))
    st.caption(
        "A student id is unique; one student can be in several courses, under several teachers. "
        "Edit a name or email in the table; the id, username and courses are fixed."
    )
    if not everyone:
        st.caption("No students yet.")
        return
    table = pd.DataFrame(everyone)[["student_id", "name", "email", "username", "courses"]]
    edited = st.data_editor(
        table, hide_index=True, width="stretch", key="students_edit",
        disabled=["student_id", "username", "courses"],
    )  # fmt: skip
    changed = [
        (old.student_id, new["name"], new["email"])
        for old, (_, new) in zip(table.itertuples(), edited.iterrows(), strict=True)
        if (old.name, old.email) != (new["name"], new["email"])
    ]
    if changed and st.button(f"Save {len(changed)} change(s) to students"):
        for sid, name, email in changed:
            students.update(sid, name or "", email or "", me)
        st.rerun()


def _rename_user(users: list[dict], me: str) -> None:
    """Change the name an account is shown under. The username never changes."""
    with st.expander("Rename an account"), st.form("rename_user", border=False):
        who = st.selectbox("Account", [u["username"] for u in users])
        name = st.text_input("Name shown")
        if st.form_submit_button("Save name"):
            auth.set_name(who, name, by=me)
            st.rerun()


def _edit_course(me: str) -> None:
    """Rename any course or change its term. The code never changes."""
    every = courses.list_courses()
    if not every:
        return
    with st.expander("Rename a course"), st.form("admin_edit_course", border=False):
        by_id = {c["id"]: c for c in every}
        cid = st.selectbox(
            "Course",
            list(by_id),
            format_func=lambda i: f"{courses.label(by_id[i])} ({by_id[i]['teacher']})",
        )
        title = st.text_input("Title", by_id[cid]["title"])
        term = st.text_input("Term", by_id[cid]["term"])
        if st.form_submit_button("Save course"):
            try:
                courses.update_course(cid, title, term, me)
            except ValueError as e:
                st.error(str(e))
            else:
                st.rerun()


# ---------- AI models ----------


def _models() -> None:
    """Which models teachers can pick; any of them can be switched off here."""
    me = session.current_user()["username"]
    st.caption("Teachers choose from the models switched on here. They see the name, use and cost.")
    with st.form("models"):
        picks: dict[str, bool] = {}
        ids: dict[str, str] = {}
        st.markdown("**Marking models**")
        for option in models.catalogue():
            ok, why = models.availability(option)
            left, right = st.columns([3, 2], vertical_alignment="center")
            with left:
                picks[option.id] = st.checkbox(
                    option.label, value=models.is_enabled(option), key=f"en_{option.id}"
                )
                st.caption(option.blurb)
                if not ok:
                    st.markdown(ui.chips((why, "red")), unsafe_allow_html=True)
            with right:
                ids[option.id] = st.text_input(
                    "Model id", value=option.model, key=f"id_{option.id}"
                )
        st.divider()
        st.markdown("**Handwriting readers**")
        reads: dict[str, bool] = {}
        for reader in models.READERS:
            ok, why = models.reader_availability(reader)
            on = bool(models._load().get("enabled", {}).get(reader.id, True))
            reads[reader.id] = st.checkbox(reader.label, value=on, key=f"en_{reader.id}")
            st.caption(reader.blurb + ("" if ok else f" Not usable now: {why}"))
        if st.form_submit_button("Save", type="primary"):
            for reader in models.READERS:
                was = bool(models._load().get("enabled", {}).get(reader.id, True))
                if was != reads[reader.id]:
                    models.set_enabled(reader.id, reads[reader.id], me)
            for option in models.catalogue():
                if models.is_enabled(option) != picks[option.id]:
                    models.set_enabled(option.id, picks[option.id], me)
                if ids[option.id].strip() != option.model:
                    models.set_model_id(option.id, ids[option.id], me)
            st.success("Saved.")
            st.rerun()


# ---------- exams and jobs ----------


def _exams() -> None:
    cards = overview.for_owner(None)
    rows = []
    for card in cards:
        job = jobs.job_state(card["id"])
        rows.append(
            {
                "exam": card["title"],
                "owner": card["owner"],
                "status": card["status"],
                "model": card["model"],
                "students": card["students"],
                "last job": f"{job.get('kind', '')} {job.get('state', '')}".strip(),
                "created": card["created"],
            }
        )
    busy = jobs.running_exam()
    c1, c2 = st.columns(2)
    c1.metric("Exams", len(rows))
    c2.metric("Marking now", busy or "nothing")
    if busy and st.button("Cancel the running job"):
        jobs.cancel(busy)
        st.rerun()
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    if cards:
        _manage_exam(cards)


def _manage_exam(cards: list[dict]) -> None:
    """Admin controls over any teacher's exam: owner, model, reader, publishing, deletion."""
    me = session.current_user()["username"]
    st.subheader("Manage an exam")
    titles = {c["id"]: f"{c['title']} ({c['owner']})" for c in cards}
    exam_id = st.selectbox("Exam", list(titles), format_func=titles.get, key="admin_exam")
    meta = storage.load_meta(exam_id)
    teachers = [u["username"] for u in auth.list_users() if u["role"] in ("teacher", "admin")]
    left, mid, right = st.columns(3)
    owner = left.selectbox(
        "Owner", teachers, index=teachers.index(meta["owner"]) if meta["owner"] in teachers else 0
    )
    model_ids = [o.id for o in models.catalogue()]
    model = mid.selectbox(
        "Marking model",
        model_ids,
        index=model_ids.index(meta["model"]) if meta["model"] in model_ids else 0,
        format_func=lambda i: models.get(i).label,
    )
    reader_ids = [r.id for r in models.READERS]
    reader = right.selectbox(
        "Handwriting reader",
        reader_ids,
        index=reader_ids.index(meta["reader"]) if meta["reader"] in reader_ids else 0,
        format_func=lambda i: models.get_reader(i).label,
    )
    a, b, c = st.columns(3)
    if a.button("Save changes", key="admin_exam_save"):
        if owner != meta["owner"]:
            meta["owner"] = owner
            storage.save_meta(exam_id, meta)
            db.audit(me, "exam_owner", f"{exam_id} -> {owner}")
        if model != meta["model"]:
            storage.set_model(exam_id, model)
        if reader != meta["reader"]:
            storage.set_reader(exam_id, reader)
        st.success("Saved.")
        st.rerun()
    if meta.get("published") and b.button("Unpublish", key="admin_exam_unpub"):
        storage.set_published(exam_id, False)
        db.audit(me, "exam_unpublished", exam_id)
        st.rerun()
    with c.popover("Delete this exam"):
        sure = st.checkbox("Delete its files, marks and regrade requests", key="admin_exam_sure")
        if st.button("Delete", disabled=not sure, key="admin_exam_del"):
            if jobs.job_state(exam_id).get("state") == "running":
                st.error("Cancel the running job first.")
            else:
                storage.delete_exam(exam_id)
                db.audit(me, "exam_deleted", exam_id)
                st.rerun()


# ---------- database ----------


def _database() -> None:
    """Browse, correct and delete records in any table, add records, and back the database up."""
    me = session.current_user()["username"]
    st.info(
        "Direct access to the portal's records. Changes are saved at once and recorded in the "
        "audit log. Take a backup before a large clean-up."
    )
    left, right = st.columns([1, 3], vertical_alignment="center")
    if left.button("Back up the database now"):
        right.success(f"Saved app_data/backups/{dbadmin.backup(me)}")
    _add_records(me)
    table = st.selectbox("Table", list(dbadmin.TABLES), key="db_table")
    frame = dbadmin.rows(table)
    st.caption(
        f"{len(frame)} row(s). Editable: {', '.join(dbadmin.editable(table)) or 'none'}. "
        + (
            "Tick 'delete' to remove a row."
            if dbadmin.deletable(table)
            else "Rows cannot be deleted here."
        )
    )
    if frame.empty:
        st.caption("Nothing in this table.")
        return
    shown = frame.assign(delete=False) if dbadmin.deletable(table) else frame
    locked = [c for c in shown.columns if c not in dbadmin.editable(table) and c != "delete"]
    edited = st.data_editor(
        shown, hide_index=True, width="stretch", disabled=locked, key=f"db_edit_{table}"
    )
    if st.button("Save changes", type="primary", key=f"db_save_{table}"):
        try:
            updated, deleted = dbadmin.apply(table, shown, edited, me)
        except ValueError as e:
            st.error(str(e))
        else:
            st.success(f"{updated} updated, {deleted} deleted.")
            st.rerun()


def _add_records(me: str) -> None:
    """Forms to create a student, a course for any teacher, or an enrolment."""
    with st.expander("Add a record"):
        c1, c2, c3 = st.tabs(["Student", "Course", "Enrolment"])
        with c1, st.form("db_add_student", clear_on_submit=True, border=False):
            sid = st.text_input("Student id (roll number)")
            name = st.text_input("Name")
            email = st.text_input("Email")
            if st.form_submit_button("Add student"):
                try:
                    students.ensure(sid, name, email)
                except ValueError as e:
                    st.error(str(e))
                else:
                    st.rerun()
        teachers = [u["username"] for u in auth.list_users() if u["role"] in ("teacher", "admin")]
        with c2, st.form("db_add_course", clear_on_submit=True, border=False):
            code, title, term = st.text_input("Code"), st.text_input("Title"), st.text_input("Term")
            teacher = st.selectbox("Teacher", teachers)
            if st.form_submit_button("Add course"):
                try:
                    courses.create_course(code, title, teacher, term, by=me)
                except ValueError as e:
                    st.error(str(e))
                else:
                    st.rerun()
        every = courses.list_courses()
        with c3, st.form("db_add_enrol", clear_on_submit=True, border=False):
            by_id = {c["id"]: c for c in every}
            cid = st.selectbox(
                "Course",
                list(by_id),
                format_func=lambda i: f"{courses.label(by_id[i])} ({by_id[i]['teacher']})",
            )
            sid = st.text_input("Student id")
            if st.form_submit_button("Enrol") and by_id:
                try:
                    courses.enrol(cid, sid, me)
                except ValueError as e:
                    st.error(str(e))
                else:
                    st.rerun()
