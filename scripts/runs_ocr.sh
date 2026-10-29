A=".venv/Scripts/autograde --config configs/experiments/ocr/ocr_noise.yaml"
# Part A: real scans -> marks, same sheets read by three readers + the hand-read truth
.venv/Scripts/python tools/ocr/ocr_pipeline_eval.py --config configs/experiments/ocr/ocr_test.yaml --out runs/ocr_test \
  --source gem35lite=runs/ocrp_gem35lite --source haiku=runs/ocrp_haiku --source sonnet=runs/ocrp_sonnet > runs/ocr_test.log 2>&1
# Part B: simulated noise, same 24 answers each
$A run --dataset digiklausur --split dev -n 24 --seed 1 --mode pipeline --name ocrn_clean --no-commit > runs/ocrn.log 2>&1
for lv in light medium heavy; do
  $A run --dataset digiklausur --split dev -n 24 --seed 1 --mode pipeline --ocr $lv --name ocrn_$lv --no-commit >> runs/ocrn.log 2>&1
done
for r in clean heavy; do
  $A revision --name ocrn_$r --sample 12 >> runs/ocrn_rev_$r.log 2>&1
  $A transfer --name ocrn_$r --sample 12 >> runs/ocrn_trn_$r.log 2>&1
done
echo done > runs/ocr_ALL_DONE.flag
