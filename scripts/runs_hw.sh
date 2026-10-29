A=".venv/Scripts/autograde --config configs/experiments/ocr/ocr_free.yaml"
$A ocr data/raw/mendeley_exam/pages_tune --per-page --out runs/ocr_mendeley_tune > runs/ocr_mendeley_tune.log 2>&1
.venv/Scripts/python tools/ocr/ocr_exam_eval.py --split tune --source gem=runs/ocr_mendeley_tune --out runs/ocr_exam_tune > runs/ocr_exam_tune.log 2>&1
echo done > runs/hw_tune_DONE.flag
