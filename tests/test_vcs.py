import subprocess
from pathlib import Path

import pytest

from autograde.evaluation.experiments import comparisons, render_markdown
from autograde.vcs import GitError, commit_experiment, commit_message, subject_line, tag_name


def entry(variant="v1", run="r1", err=0.2, mode="pipeline", cost=0.5, ts="2026-10-15T10:00:00"):
    return {
        "ts": ts,
        "variant": variant,
        "note": "reads first",
        "run": run,
        "dataset": "d",
        "split": "dev",
        "n": 24,
        "seed": 0,
        "mode": mode,
        "model": "fake-m",
        "pipeline": {"read_first": True},
        "prompts": {"all": "abc12345"},
        "overall": {
            "mean_abs_error": err,
            "bias": -0.1,
            "pearson": 0.8,
            "qwk": 0.6,
            "same_level": 0.5,
        },
        "by_band": {"mid": {"n": 5, "mean_abs_error": 0.3}},
        "flagged_share": 0.1,
        "cost_usd": cost,
        "calls": 10,
    }


def test_subject_line_carries_the_scores():
    s = subject_line(entry())
    assert s.startswith("exp(v1): error 0.200 | bias -0.100 | r 0.80 | qwk 0.60 | $0.50")
    assert s.endswith("[d/dev n=24 seed=0]")


def test_message_has_full_detail():
    m = commit_message(entry(), "better", "-")
    assert "vs baseline better" in m and "prompts:  abc12345" in m and "mid: n=5" in m


def test_tag_names_are_safe():
    assert tag_name("v1 read/first", "dk run#2") == "exp-v1-read-first-dk-run-2"


def test_comparisons_use_the_same_sample_only():
    rows = [
        entry("baseline", "b", 0.3, "baseline"),
        entry("v0", "p0", 0.25),
        entry("v1", "p1", 0.2),
    ]
    vs_base, vs_prev = comparisons(rows, 2)
    assert vs_base.endswith("-0.100") and vs_prev.endswith("-0.050")
    other = dict(entry("v2", "p2", 0.1), seed=9)
    assert comparisons([*rows, other], 3) == ("-", "-")


def test_markdown_table_lists_every_run():
    md = render_markdown([entry("baseline", "b", 0.3, "baseline"), entry("v1", "p1", 0.2)])
    assert "| baseline | b |" in md and "| v1 | p1 |" in md
    assert "-0.100" in md  # the change against the baseline


def init_repo(path: Path) -> None:
    for cmd in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", *cmd], cwd=path, check=True)


def git_out(path: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=path, capture_output=True, text=True, check=True
    ).stdout


def test_commit_and_tag_in_a_real_repo(tmp_path: Path):
    init_repo(tmp_path)
    (tmp_path / "code.py").write_text("x = 1\n")
    tag = commit_experiment(entry(), "-", "-", tmp_path)
    assert tag == "exp-v1-r1"
    assert "exp(v1): error 0.200" in git_out(tmp_path, "log", "--format=%s")
    assert "Scores against the teacher" in git_out(tmp_path, "tag", "-n99", "-l", tag)
    (tmp_path / "code.py").write_text("x = 2\n")
    assert commit_experiment(entry(), "-", "-", tmp_path) != tag  # same names, new tag


def test_not_a_repo_is_reported(tmp_path: Path):
    with pytest.raises(GitError):
        commit_experiment(entry(), "-", "-", tmp_path)
