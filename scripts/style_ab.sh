#!/bin/sh
# Scheme style A/B. Tuned on Mohler dev seed 1; checked on other samples and other datasets
# (seed 7) that the style was not written against. One DeepSeek job at a time (Goedel allows 4).
cd "$(dirname "$0")/.." || exit 1
run() { # config dataset seed name
  .venv/Scripts/autograde --config "configs/experiments/style/$1.yaml" run --dataset "$2" --split dev -n 30 \
    --seed "$3" --mode pipeline --name "$4" --no-commit > "runs/$4.log" 2>&1
}
run style_fine mohler 1 ab_mohler_s1_fine
run style_core mohler 1 ab_mohler_s1_core
for D in mohler digiklausur ricechem; do
  run style_fine $D 7 ab_${D}_s7_fine
  run style_core $D 7 ab_${D}_s7_core
done
echo done > runs/ab_DONE.flag
