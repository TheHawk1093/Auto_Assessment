export PYTHONIOENCODING=utf-8
for d in asap_sas scientsbank aes2 processbench; do
  .venv/Scripts/autograde --config configs/cmp_new.yaml run --dataset $d --split dev -n 30 --seed 1 --mode pipeline --name new_pipeline_$d > /dev/null 2>&1
  .venv/Scripts/autograde --config configs/cmp_new.yaml run --dataset $d --split dev -n 30 --seed 1 --mode baseline --name new_baseline_$d > /dev/null 2>&1
done
