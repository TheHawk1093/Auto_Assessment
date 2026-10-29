#!/bin/sh
# Robustness test on four finished marking runs: Mohler, DigiKlausur and RiceChem (English, 30
# answers each, scheme style "solid") and translated Mohler in Hindi. Every perturbation, plus the
# unchanged answer re-marked as the noise control. One DeepSeek job at a time.
cd "$(dirname "$0")/.." || exit 1
S=configs/experiments/style/style_fine.yaml
run() { # config run (skipped when its result exists, so the chain can be resumed)
  [ -f "runs/$2/robustness.json" ] && return
  .venv/Scripts/autograde --config "$1" robustness --name "$2" > "runs/robust_$2.log" 2>&1
}
run $S ab_mohler_s7_fine
run $S ab_digiklausur_s7_fine
run $S ab_ricechem_s7_fine
run configs/experiments/indic/tr_hindi.yaml tr2_hindi
echo done > runs/robust_DONE.flag
