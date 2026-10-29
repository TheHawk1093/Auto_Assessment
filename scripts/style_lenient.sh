#!/bin/sh
# Teacher-setting check: does strictness "lenient" move marks towards a lenient teacher (Mohler)
# and away from a strict one (RiceChem)? Runs after scripts/style_fit.sh.
cd "$(dirname "$0")/.." || exit 1
while [ ! -f runs/fit_DONE.flag ]; do sleep 30; done
run() { # dataset seed
  .venv/Scripts/autograde --config configs/experiments/style/style_lenient.yaml run --dataset "$1" --split dev -n 30 \
    --seed "$2" --mode pipeline --name ab_$1_s$2_len --no-commit > runs/ab_$1_s$2_len.log 2>&1
}
run mohler 1; run mohler 7; run ricechem 7; run digiklausur 7
echo done > runs/len_DONE.flag
