# Kiko v2 upgrade evidence

This directory records the validated upgrade from Kiko's original 8×9 pet atlas to the 8×11 v2 contract.

- `validation.json` — structural validation of the packaged `kiko/spritesheet.webp`
- `qa/contact-sheet.png` — all nine animation rows plus two direction rows
- `qa/look-directions.png` — neutral pose and all 16 labeled directions
- `qa/look-mechanics.md` — character-specific gaze mechanics
- `qa/repair-log.json` — rejected direction-row attempts and the accepted repair
- `qa/direction-semantics.json` — labeled semantic verdict for every direction
- `qa/direction-blind-validation.json` — combined three-reviewer blind axis check
- `qa/look-continuity.json` — adjacent-pose continuity evidence
- `qa/standard-visual-qa.json` — review of the preserved nine animation rows
- `qa/final-visual-qa.json` — final independent visual acceptance

The packaged atlas has `spriteVersionNumber: 2`, dimensions `1536 × 2288`, transparent unused cells, and no validation errors or warnings.

Running `scripts/rebuild-atlas.sh` writes a fresh machine-local check to the ignored `validation-local.json`; the committed `validation.json` remains the portable acceptance record.
