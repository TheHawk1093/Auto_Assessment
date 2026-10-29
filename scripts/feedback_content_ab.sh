#!/bin/sh
# Feedback content and system prompt: "formal" (tr2_*) against "concrete" v2 (fb3_*: concrete fix,
# a real reason, length matched to the marks lost, no "wrong" for a true statement). The marks are
# the finished tr2_* runs, so only the feedback differs. Written looking at English only; the other
# languages and real Marathi are the check. The student who rewrites is the weakest model
# (Gemini Flash Lite). One DeepSeek job at a time (Goedel allows 4 requests).
cd "$(dirname "$0")/.." || exit 1
one() { # language marks-run config-for-weak-student judge-config
  L=$1; SRC=$2; WEAK=$3; BASE=$4
  .venv/Scripts/autograde --config "$BASE" refeedback --name "$SRC" --new-name "fb3_$L" \
    --feedback concrete --variant concrete2 --no-commit > "runs/fb3_$L.log" 2>&1
  .venv/Scripts/autograde --config "$BASE" judge --name "fb3_$L" > "runs/fb3_${L}_judge.log" 2>&1
  .venv/Scripts/autograde --config "$WEAK" revision --name "fb3_$L" > "runs/fb3_${L}_revision.log" 2>&1
  mv "runs/fb3_$L/revision_scores.json" "runs/fb3_$L/revision_scores_weak.json"
  [ -f "runs/$SRC/revision_scores_haiku.json" ] || cp "runs/$SRC/revision_scores.json" "runs/$SRC/revision_scores_haiku.json"
  .venv/Scripts/autograde --config "$WEAK" revision --name "$SRC" > "runs/${SRC}_revision_weak.log" 2>&1
  cp "runs/$SRC/revision_scores.json" "runs/$SRC/revision_scores_weak.json"
}
I=configs/experiments/indic
F=configs/experiments/feedback
one english tr2_english $F/weak_english.yaml $I/tr_english.yaml
one hindi tr2_hindi $F/weak_hindi.yaml $I/tr_hindi.yaml
one marathi tr2_marathi $F/weak_marathi.yaml $I/tr_marathi.yaml
one tamil tr2_tamil $F/weak_tamil.yaml $I/tr_tamil.yaml
one bengali tr2_bengali $F/weak_bengali.yaml $I/tr_bengali.yaml
one scaa_mr scaa_mr_ds $F/weak_scaa_mr.yaml $I/indic_mr_deepseek.yaml
echo done > runs/fb3_DONE.flag
