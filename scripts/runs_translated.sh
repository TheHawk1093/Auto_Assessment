cd "d:/IITM ED/Acads/Sem 9/Auto_Assessment"
.venv/Scripts/python -m autograde.datasets.translate --dataset mohler -n 30 > runs/tr_translate.log 2>&1
for L in english hindi marathi tamil bengali; do
  C=".venv/Scripts/autograde --config configs/tr_$L.yaml"
  $C run --dataset mohler_$L --split dev -n 30 --mode pipeline --name tr_$L --no-commit > runs/tr_$L.log 2>&1
  $C judge --name tr_$L > runs/tr_${L}_judge.log 2>&1
  $C revision --name tr_$L > runs/tr_${L}_revision.log 2>&1
done
echo done > runs/tr_DONE.flag
