# Data credits

Only the datasets the tuning workflow actually uses are listed. Raw data is fetched with
`autograde download`, never stored whole in git. The `dev` branch ships a few dozen sample rows
per dataset (see `datasets/samples/`) so the loaders and tests run offline. All rights stay with the
original authors; follow each licence when you use or redistribute the data.

| Dataset | Used for | Authors / source | Licence | Shipped as |
|---|---|---|---|---|
| DigiKlausur ASAG | Dev smoke test, full-exam shape | DigiKlausur project, [repo](https://github.com/DigiKlausur/ASAG-Dataset) | MPL-2.0 (LICENSE in the repo) | sample rows |
| SAF (Short Answer Feedback) | Feedback quality, feedback judge | Filighera, Ochs et al., ACL 2022, [paper](https://aclanthology.org/2022.acl-long.587/), [repo](https://github.com/SebOchs/SAF) | Code MIT; data licence not stated in the repo | download only |
| Mohler 2011 | Short-answer baseline | Mohler, Bunescu, Mihalcea, ACL 2011, [paper](https://aclanthology.org/P11-1076/) | CC-BY-4.0 (Hugging Face card) | sample rows |
| EngSAF | Benchmark only, never tuned on | Hugging Face dataset `engsaf` | Apache-2.0 (dataset card) | download only |
| RiceChem | Long-answer grading, optional | Chen et al., [paper](https://arxiv.org/abs/2404.14316), [repo](https://github.com/luffycodes/Automated-Long-Answer-Grading) | None stated; access by request | not distributed |

Private course material (for example the ME5309 exam and answer sheets) is never part of either
branch.
