#!/bin/sh
# Feedback A/B: "formal" (the default) against "concrete" (a concrete fix, a real reason in why).
# Marks and schemes are the finished tr2_* runs, so only the feedback differs. English was used to
# write the change; the other languages and real Marathi (ScAA) were not looked at. One DeepSeek
# job at a time (Goedel allows 4 requests).
cd "$(dirname "$0")/.." || exit 1
one() { # config source-run new-run
  C=".venv/Scripts/autograde --config $1"
  $C refeedback --name "$2" --new-name "$3" --feedback concrete --variant concrete \
    --no-commit > "runs/$3.log" 2>&1
  $C judge --name "$3" > "runs/$3_judge.log" 2>&1
  $C revision --name "$3" > "runs/$3_revision.log" 2>&1
}
for L in english hindi marathi tamil bengali; do
  one "configs/experiments/indic/tr_$L.yaml" "tr2_$L" "fb2_$L"
done
one configs/experiments/indic/indic_mr_deepseek.yaml scaa_mr_ds fb2_scaa_mr
echo done > runs/fb2_DONE.flag
