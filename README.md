# Kiko Codex pet (v2)

Kiko is a cute color-changing gecko for Codex Desktop. Kiko keeps one recognizable gecko identity while changing body color, expression, and motion to reflect the current task condition. This repository packages Kiko as a v2 pet with 16 pointer-responsive look directions.

![Kiko's complete v2 contact sheet](run/v2/qa/contact-sheet.png)

## Install

Copy the `kiko/` directory into your local Codex pets folder:

```bash
mkdir -p ~/.codex/pets/kiko
cp kiko/pet.json kiko/spritesheet.webp ~/.codex/pets/kiko/
```

Or run:

```bash
./scripts/install.sh
```

If Kiko does not appear immediately, reopen the pet picker or restart Codex Desktop.

The manifest explicitly sets `"spriteVersionNumber": 2`. While Kiko is awake as the floating desktop pet, move the pointer around Kiko to select the directional poses. Look tracking is used during idle, running, and waving; special status animations take priority.

## Condition map

| Codex state | Frames | Kiko color | Expression and motion |
|---|---:|---|---|
| `idle` | 6 | Mint green | Calm smile, breathing bob, blink |
| `running-right` | 8 | Aqua | Determined rightward scurry |
| `running-left` | 8 | Aqua | Determined leftward scurry |
| `waving` | 4 | Sunny yellow | Cheerful hand wave |
| `jumping` | 5 | Coral orange | Thrilled vertical hop |
| `failed` | 8 | Soft blue | Gentle droop and recovery |
| `waiting` | 6 | Warm amber | Patient, empty-hands asking pose |
| `running` | 6 | Teal | Prop-free focused work loop |
| `review` | 6 | Lavender | Skeptical squint, head tilt, chin touch |

## Look directions

The first nine rows preserve Kiko's original animations. Rows 9 and 10 add 16 clockwise look poses in 22.5-degree steps:

- row 9: `000` up through `157.5` down-right
- row 10: `180` down through `337.5` up-left

Kiko's feet and lower body stay anchored while the complete eyes lead, followed by restrained head and neck movement. The focused direction sheet is available at [`run/v2/qa/look-directions.png`](run/v2/qa/look-directions.png).

The finished v2 atlas follows the Codex extended pet contract: an 8-column by 11-row `1536 × 2288` RGBA WebP made from `192 × 208` cells. Unused cells are fully transparent.

## Repository contents

- `kiko/` — the two-file installable pet package
- `run/decoded/` — accepted generated base and raw state strips
- `run/decoded-clean/` — alpha-clean, despilled source strips
- `run/rejected/` — rejected iterations kept to document repair decisions
- `run/prompts/` — generated base, row, and retry prompts
- `run/references/` — canonical Kiko base and layout guides
- `run/frames/` — extracted `192 × 208` animation frames
- `run/final/` — reproducible 8×9 standard-animation intermediate
- `run/qa/` — original nine-state contact sheet, GIF previews, and QA JSON
- `run/v2/` — v2 validation and directional QA evidence
- `notes-on-creating-kiko.md` — detailed workflow notebook
- `scripts/install.sh` — local installer
- `scripts/rebuild-atlas.sh` — deterministic rebuild from cleaned strips

## Rebuild

The source strips for Kiko's nine standard animations are already generated. If the OpenAI `hatch-pet` skill is installed, rebuild that intermediate and revalidate the packaged v2 atlas with:

```bash
./scripts/rebuild-atlas.sh
```

Set `PYTHON` to a Python executable with Pillow if `python3` is not on your path. The script deliberately never overwrites `kiko/spritesheet.webp` with the 8×9 intermediate.

Image generation is intentionally not automated because generated artwork is stochastic and every row needs visual review. The accepted standard-row prompts and images remain under `run/`; the v2 direction mechanics, repair log, semantic review, blind validation, continuity report, contact sheet, and final validation are preserved under `run/v2/`.

## Credits

This repository was inspired by Simon Willison's [simonw/pedalican](https://github.com/simonw/pedalican) and his [write-up about hatching a Codex pet](https://simonwillison.net/2026/Jul/14/pedalican/).
