cd "d:/IITM ED/Acads/Sem 9/Auto_Assessment"
until [ -f runs/mend_ALL_DONE.flag ]; do sleep 20; done
timeout 2400 .venv/Scripts/python tools/ocr/ocr_exam_eval.py --split tune --source gem=runs/ocr_mendeley_tune --config configs/experiments/ocr/ocr_test_harsh.yaml --out runs/ocr_exam_tune_harsh > runs/ocr_exam_tune_harsh2.log 2>&1
echo done > runs/harsh_DONE.flag
