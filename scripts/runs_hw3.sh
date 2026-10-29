.venv/Scripts/autograde --config configs/experiments/ocr/ocr_free.yaml ocr data/raw/mendeley_exam/pages_validate --per-page --out runs/ocr_mendeley_validate > runs/ocr_mendeley_validate.log 2>&1
n=$(ls runs/ocr_mendeley_validate/*.sheet.json 2>/dev/null | wc -l)
if [ "$n" -ge 30 ]; then
  .venv/Scripts/python tools/ocr/ocr_exam_eval.py --split validate --source gem=runs/ocr_mendeley_validate --out runs/ocr_exam_validate > runs/ocr_exam_validate.log 2>&1
else
  echo "reading incomplete: $n sheets" > runs/ocr_exam_validate.log
fi
echo done > runs/hw_validate_DONE.flag
