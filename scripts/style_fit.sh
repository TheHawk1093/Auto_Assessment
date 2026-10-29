#!/bin/sh
# Second samples (seed 1) for the calibration check: fit the stretch on seed 1, apply it to the
# seed 7 runs of scripts/style_ab.sh. Waits for that script to finish: one DeepSeek job at a time.
cd "$(dirname "$0")/.." || exit 1
while [ ! -f runs/ab_DONE.flag ]; do sleep 30; done
for D in digiklausur ricechem; do
  .venv/Scripts/autograde --config configs/experiments/style/style_core.yaml run --dataset $D --split dev -n 30 \
    --seed 1 --mode pipeline --name ab_${D}_s1_core --no-commit > runs/ab_${D}_s1_core.log 2>&1
done
echo done > runs/fit_DONE.flag
