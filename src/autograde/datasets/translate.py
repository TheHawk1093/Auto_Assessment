"""English datasets translated into other languages, to test marking and feedback in them.

The same sample of answers is translated into each language, so results are comparable across
languages (and with English). The marks are the original teacher marks: translation is assumed to
keep the quality of an answer, which is the weakness of this test (a translated answer reads more
fluently than a child's or a non-native writer's own). Translations are cached in
`data/raw/translated/<dataset>_<language>.json`, and the loader reads only that cache.

Run: `python -m autograde.datasets.translate --dataset mohler --languages Hindi Tamil -n 30`.
"""

from __future__ import annotations

import argparse
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pydantic import BaseModel

from autograde import prompts
from autograde.llm import LLMClient
from autograde.schemas import Item

log = logging.getLogger(__name__)
LANGUAGES = ("English", "Hindi", "Marathi", "Tamil", "Bengali")  # English: the same sample, as is
BASES = ("mohler", "digiklausur")


class Translated(BaseModel):
    question: str
    model_answer: str
    student_answer: str


def cache_path(data_dir: Path, base: str, language: str) -> Path:
    return data_dir / "translated" / f"{base}_{language.lower()}.json"


def translate_item(item: Item, language: str, client: LLMClient) -> Item:
    if language == "English":  # the control: the same items, untouched
        return item.model_copy(
            update={"dataset": f"{item.dataset}_english", "id": f"{item.id}@english"}
        )
    user = (
        f"Target language: {language}\n\nQuestion:\n{item.question}\n\n"
        f"Model answer:\n{item.model_answer}\n\nStudent's answer:\n{item.student_answer}"
    )
    out = client.ask(prompts.system("translate.out"), user, Translated)
    return item.model_copy(
        update={
            "question": out.question,
            "model_answer": out.model_answer,
            "student_answer": out.student_answer,
            "dataset": f"{item.dataset}_{language.lower()}",
            "id": f"{item.id}@{language.lower()}",
        }
    )


def build(
    base: str, language: str, items: list[Item], client: LLMClient, data_dir: Path, workers: int = 3
) -> int:
    """Translate `items` (skipping those already cached); returns how many were translated."""
    path = cache_path(data_dir, base, language)
    have = {i.id: i for i in _read(path)}
    todo = [i for i in items if f"{i.id}@{language.lower()}" not in have]
    with ThreadPoolExecutor(workers) as pool:
        for done in pool.map(lambda i: translate_item(i, language, client), todo):
            have[done.id] = done
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps([i.model_dump() for i in have.values()], ensure_ascii=False), encoding="utf-8"
    )
    return len(todo)


def _read(path: Path) -> list[Item]:
    if not path.exists():
        return []
    return [Item.model_validate(d) for d in json.loads(path.read_text(encoding="utf-8"))]


def loader(base: str, language: str):
    def load(data_dir: Path) -> list[Item]:
        return _read(cache_path(data_dir, base, language))

    return load


def main() -> None:
    from autograde.config import load_settings
    from autograde.datasets.loaders import load_dataset, select
    from autograde.llm import build_client

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--config", type=Path, default=Path("configs/experiments/indic/indic_mr_deepseek.yaml")
    )
    ap.add_argument("--dataset", choices=BASES, default="mohler")
    ap.add_argument("--languages", nargs="+", default=list(LANGUAGES))
    ap.add_argument("-n", type=int, default=30)
    args = ap.parse_args()
    settings = load_settings(args.config)
    items = select(load_dataset(args.dataset, settings.paths.data_dir), "dev", args.n, seed=1)
    client = build_client(settings.llm)
    for language in args.languages:
        made = build(args.dataset, language, items, client, settings.paths.data_dir)
        print(f"{language}: translated {made} of {len(items)}")


if __name__ == "__main__":
    main()
