from autograde import prompts


def test_prompt_names_are_unique_across_folders():
    root = prompts.resources.files(prompts.__package__)
    names = [
        p.name
        for folder in root.iterdir()
        if folder.is_dir() and not folder.name.startswith("__")
        for p in folder.iterdir()
        if p.name.endswith(".md")
    ]
    assert len(names) == len(set(names)) == len(prompts._index())


def test_a_prompt_is_found_by_name_whatever_its_folder():
    assert "marking scheme" in prompts.system("rubric.solid")
    assert prompts.optional("language.hindi")
    assert prompts.optional("no.such.prompt") == ""


def test_experiment_log_fingerprints_every_prompt_file():
    from autograde.evaluation.experiments import prompt_fingerprint

    fp = prompt_fingerprint()
    assert "rubric.solid.system.md" in fp and "language.hindi.system.md" in fp
    assert len(fp) == len(prompts.files()) + 1
