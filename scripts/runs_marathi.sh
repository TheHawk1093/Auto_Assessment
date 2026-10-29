cd "d:/IITM ED/Acads/Sem 9/Auto_Assessment"
A=".venv/Scripts/autograde --config configs/experiments/indic/indic_gemini_mr.yaml run --dataset scaa_marathi --split dev -n 24 --no-commit"
$A --mode baseline --name scaa_mr_baseline > runs/scaa_mr_baseline.log 2>&1
$A --mode pipeline --name scaa_mr_pipeline > runs/scaa_mr_pipeline.log 2>&1
echo done > runs/scaa_mr_DONE.flag
