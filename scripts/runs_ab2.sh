A=".venv/Scripts/autograde --config configs/experiments/compare/ab_feedback.yaml"
for d in digiklausur scientsbank asap_sas mohler; do
  [ $d != digiklausur ] && $A run --dataset $d --split dev -n 24 --mode pipeline --name ab_$d --no-commit > runs/ab2_$d.log 2>&1
  $A feedback-ab --name ab_$d --sample 16 >> runs/ab2_$d.log 2>&1
done
echo done > runs/ab2_DONE.flag
