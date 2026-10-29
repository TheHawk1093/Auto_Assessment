cd "d:/IITM ED/Acads/Sem 9/Auto_Assessment"
for L in english hindi marathi tamil bengali; do
  C=".venv/Scripts/autograde --config configs/tr_$L.yaml"
  $C run --dataset mohler_$L --split dev -n 30 --mode pipeline --name tr2_$L --no-commit > runs/tr2_$L.log 2>&1
  $C judge --name tr2_$L > runs/tr2_${L}_judge.log 2>&1
  $C revision --name tr2_$L > runs/tr2_${L}_revision.log 2>&1
done
C=".venv/Scripts/autograde --config configs/experiments/indic/indic_mr_deepseek.yaml"
$C revision --name scaa_mr_ds > runs/scaa_mr_ds_revision2.log 2>&1
$C --help > /dev/null 2>&1
.venv/Scripts/autograde --config configs/experiments/circuit/circuit_deepseek.yaml run --dataset circuit_hw --split dev -n 30 --mode pipeline --name circuit_dev_ds --no-commit > runs/circuit_dev_ds.log 2>&1
echo done > runs/tr2_DONE.flag
