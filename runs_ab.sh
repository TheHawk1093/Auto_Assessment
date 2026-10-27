set -x
A=".venv/Scripts/autograde --config configs/ab_feedback.yaml"
for d in scientsbank asap_sas mohler; do
  ( $A run --dataset $d --split dev -n 24 --mode pipeline --name ab_$d --no-commit > runs/ab_$d.log 2>&1 && $A feedback-ab --name ab_$d --sample 16 >> runs/ab_$d.log 2>&1 ) &
done
( $A feedback-ab --name ab_digiklausur > runs/ab_digiklausur_full.log 2>&1 ) &
wait
echo done > runs/ab_ALL_DONE.flag
