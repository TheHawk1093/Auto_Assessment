cd "d:/IITM ED/Acads/Sem 9/Auto_Assessment"
C=".venv/Scripts/autograde --config configs/experiments/indic/indic_mr_deepseek.yaml"
$C run --dataset scaa_marathi --split dev -n 24 --mode pipeline --name scaa_mr_ds --no-commit > runs/scaa_mr_ds.log 2>&1
$C judge --name scaa_mr_ds > runs/scaa_mr_ds_judge.log 2>&1
$C revision --name scaa_mr_ds > runs/scaa_mr_ds_revision.log 2>&1
echo done > runs/scaa_mr_ds_DONE.flag
