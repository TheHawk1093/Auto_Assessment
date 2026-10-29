cd "d:/IITM ED/Acads/Sem 9/Auto_Assessment"
P=data/raw/indic_words/pages_tune
A=".venv/Scripts/autograde --config configs/experiments/ocr/ocr_free.yaml ocr $P --per-page"
$A --provider gemini --model gemini-3.1-flash-lite --plain --out runs/indic_tune_g31 > runs/indic_g31.log 2>&1 &
$A --provider openrouter --model "dots-studio/dots-3-note-preview:free" --plain --out runs/indic_tune_dots > runs/indic_dots.log 2>&1 &
$A --model sonnet --out runs/indic_tune_sonnet > runs/indic_sonnet.log 2>&1 &
$A --model haiku --out runs/indic_tune_haiku > runs/indic_haiku.log 2>&1 &
$A --out runs/indic_tune_chain > runs/indic_chain.log 2>&1 &
# Mendeley grading (DeepSeek, quota is back): Sonnet-read text, then the two strictness levels
E=".venv/Scripts/python tools/ocr/ocr_exam_eval.py --split tune"
( $E --source gem=runs/ocr_mendeley_tune --source sonnet=runs/ocr_mendeley_tune_sonnet --out runs/ocr_exam_tune_cmp > runs/ocr_exam_tune_cmp2.log 2>&1
  for lv in harsh lenient; do
    $E --source gem=runs/ocr_mendeley_tune --config configs/ocr_test_$lv.yaml --out runs/ocr_exam_tune_$lv > runs/ocr_exam_tune_$lv.log 2>&1
  done
  echo done > runs/mend_ALL_DONE.flag ) &
wait
.venv/Scripts/python tools/ocr/indic_ocr_eval.py --truth data/raw/indic_words/truth_tune.json \
  --source gemini35=runs/indic_tune_g35 --source gemini31=runs/indic_tune_g31 \
  --source dots3=runs/indic_tune_dots --source sonnet=runs/indic_tune_sonnet \
  --source haiku=runs/indic_tune_haiku --source chain=runs/indic_tune_chain > runs/indic_scores_tune.txt 2>&1
echo done > runs/par_ALL_DONE.flag
