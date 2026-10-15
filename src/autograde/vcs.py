"""Git side of the experiment workflow.

Every test against the teacher's marks becomes one commit whose subject line carries the scores,
plus an annotated tag with the full message. Then:

    git tag -n1 -l "exp-*"             list every experiment with its scores
    git show exp-<variant>-<run>       open the full message and the code change
    git checkout exp-<variant>-<run>   restore the exact code that produced those scores

Nothing is pushed. Add a remote yourself and use `git push --follow-tags`.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


class GitError(RuntimeError):
    pass


def _git(args: list[str], cwd: Path) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", check=False
    )
    if proc.returncode != 0:
        raise GitError(f"git {' '.join(args)}: {(proc.stderr or proc.stdout).strip()[:300]}")
    return proc.stdout.strip()


def is_repo(cwd: Path) -> bool:
    try:
        return _git(["rev-parse", "--is-inside-work-tree"], cwd) == "true"
    except (GitError, FileNotFoundError):
        return False


def tag_name(variant: str, run: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", f"{variant}-{run}").strip("-.")
    return f"exp-{safe}"


def _num(o: dict, key: str, digits: int = 3, sign: bool = False) -> str:
    v = o.get(key)
    if v is None:
        return "n/a"
    return f"{v:+.{digits}f}" if sign else f"{v:.{digits}f}"


def subject_line(entry: dict) -> str:
    """One line with the scores, readable in `git log --oneline`."""
    o = entry["overall"]
    cost = entry.get("cost_usd")
    cost_text = "n/a" if cost is None else f"${cost:.2f}"
    return (
        f"exp({entry['variant']}): error {_num(o, 'mean_abs_error')} "
        f"| bias {_num(o, 'bias', sign=True)} | r {_num(o, 'pearson', 2)} "
        f"| qwk {_num(o, 'qwk', 2)} | {cost_text} "
        f"[{entry['dataset']}/{entry['split']} n={entry['n']} seed={entry['seed']}]"
    )


def commit_message(entry: dict, vs_base: str, vs_prev: str) -> str:
    o = entry["overall"]
    bands = ", ".join(
        f"{b}: n={v['n']} error={v['mean_abs_error']:.3f}"
        for b, v in entry.get("by_band", {}).items()
        if v.get("n") and v.get("mean_abs_error") is not None
    )
    settings = ", ".join(f"{k}={v}" for k, v in entry.get("pipeline", {}).items())
    lines = [
        subject_line(entry),
        "",
        f"variant:  {entry['variant']}",
        f"note:     {entry.get('note') or '-'}",
        f"run:      {entry['run']} ({entry['mode']}, {entry['model']})",
        f"sample:   {entry['dataset']}/{entry['split']} n={entry['n']} seed={entry['seed']}",
        f"settings: {settings or '-'}",
        f"prompts:  {entry['prompts']['all']}",
        "",
        "Scores against the teacher's marks (error = average gap, share of total marks):",
        f"  error {_num(o, 'mean_abs_error')}   vs baseline {vs_base}   vs previous {vs_prev}",
        f"  bias {_num(o, 'bias', sign=True)} (below 0 = stricter than the teacher)",
        f"  correlation {_num(o, 'pearson', 2)}   qwk {_num(o, 'qwk', 2)}"
        f"   same level {_num(o, 'same_level', 2)}",
        f"  by quality band: {bands or '-'}",
        f"  flagged {entry.get('flagged_share')}   calls {entry.get('calls')}"
        f"   cost ${entry.get('cost_usd')}",
    ]
    return "\n".join(lines)


def commit_experiment(entry: dict, vs_base: str, vs_prev: str, repo: Path = Path(".")) -> str:
    """Commit everything not ignored, then tag the commit. Returns the tag name."""
    if not is_repo(repo):
        raise GitError("not inside a git repository (run `git init` first)")
    message = commit_message(entry, vs_base, vs_prev)
    _git(["add", "-A"], repo)
    _git(["commit", "-m", message, "--allow-empty"], repo)
    name = tag_name(entry["variant"], entry["run"])
    if _git(["tag", "-l", name], repo):
        stamp = re.sub(r"\D", "", entry["ts"])[:12]
        name = f"{name}-{stamp}"
    _git(["tag", "-a", name, "-m", message], repo)
    return name


def history(repo: Path = Path(".")) -> str:
    """Experiment tags with the first line of their message."""
    return _git(["tag", "-l", "exp-*", "-n1", "--sort=creatordate"], repo)
