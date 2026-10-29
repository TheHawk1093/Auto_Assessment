# Checking the feedback judge

`judge_sheet.csv` has 60 feedbacks (Hindi, Marathi, Tamil, Bengali, English; 30 answers, each with
two feedback variants, shown in mixed order) and what the Haiku judge answered. A person who reads
the language fills the `human_*` columns with `y` or `n` for the same six questions (see
`prompts/eval/judge.system.md`). Then:

```
autograde judge-agreement --sheet artifacts/judge_check/judge_sheet.csv
```

prints, for each question, how often the person agrees with the judge and Cohen's kappa. Kappa
under about 0.4 on a question means the judge's pass rate for it should not be trusted. Leave a
cell empty to skip it. The `run` column says which variant a row is (`tr2_*` is `formal`, `fb2_*` is
`concrete`); fill the other columns first to stay unbiased.
