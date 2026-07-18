# Kiko v2 upgrade evidence

This directory contains current machine-generated evidence for Kiko's packaged 8×11 v2 atlas and historical manual-review records from the original v2 upgrade.

- `validation.json` — structural validation of the packaged `kiko/spritesheet.webp`
- `qa/contact-sheet.png` — all nine animation rows plus two direction rows
- `qa/look-directions.png` — neutral pose and all 16 labeled directions
- `qa/look-mechanics.md` — character-specific gaze mechanics from the original upgrade
- `qa/repair-log.json` — historical rejected direction-row attempts and accepted repair
- `qa/direction-semantics.json` — historical labeled semantic verdicts
- `qa/direction-blind-validation.json` — historical three-reviewer blind axis check
- `qa/look-continuity.json` — historical adjacent-pose continuity evidence
- `qa/standard-visual-qa.json` — historical review of the standard animation rows
- `qa/final-visual-qa.json` — historical independent visual acceptance

The packaged atlas has `spriteVersionNumber: 2`, dimensions `1536 × 2288`, six idle frames, transparent unused cells, and no structural validation errors or warnings.

Run `python3 scripts/update-v2-assets.py` after replacing the packaged spritesheet. It rewrites `validation.json`, `qa/contact-sheet.png`, and `qa/look-directions.png` directly from `kiko/spritesheet.webp`. Manual semantic and continuity records are intentionally historical unless a new review explicitly replaces them.
