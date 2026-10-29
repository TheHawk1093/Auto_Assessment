cd "d:/IITM ED/Acads/Sem 9/Auto_Assessment"
.venv-ocr/Scripts/python tools/ocr/compose_indic_pages.py data/raw/indic_words > runs/indic_compose.log 2>&1
P=data/raw/indic_words/pages_tune
A=".venv/Scripts/autograde --config configs/experiments/ocr/ocr_free.yaml ocr $P --per-page"
$A --provider gemini --model gemini-3.5-flash-lite --plain --out runs/indic_tune_g35 > runs/indic_g35.log 2>&1
$A --provider gemini --model gemini-3.1-flash-lite --plain --out runs/indic_tune_g31 > runs/indic_g31.log 2>&1
$A --provider openrouter --model "dots-studio/dots-3-note-preview:free" --plain --out runs/indic_tune_dots > runs/indic_dots.log 2>&1
$A --model sonnet --out runs/indic_tune_sonnet > runs/indic_sonnet.log 2>&1
$A --out runs/indic_tune_chain > runs/indic_chain.log 2>&1
.venv/Scripts/python tools/ocr/indic_ocr_eval.py --truth data/raw/indic_words/truth_tune.json \
  --source gemini35=runs/indic_tune_g35 --source gemini31=runs/indic_tune_g31 \
  --source dots3=runs/indic_tune_dots --source sonnet=runs/indic_tune_sonnet \
  --source chain=runs/indic_tune_chain > runs/indic_scores_tune.txt 2>&1
echo done > runs/indic_ALL_DONE.flag
