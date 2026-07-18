# Notes on creating the Kiko Codex pet

Last updated: 2026-07-18 (Asia/Bangkok)

## Goal

Create, install, validate, and package a custom animated Codex pet: a cute gecko that changes color and expression with task conditions. Preserve the complete Codex nine-state animation contract and keep the whole workflow shareable.

## Final identity

Kiko is an original upright baby gecko with:

- a slim narrow torso and long neck-to-belly line
- a softly wedge-shaped head rather than a round mascot head
- huge warm dark eyes, tiny nostrils, and a confident small smile
- a cream throat and belly
- pale cheek freckles and darker crown/back speckles
- short splayed limbs with rounded adhesive toe pads
- a long low tail that curves beside the body
- a softly modeled kawaii 3D-sticker rendering

The user-provided reference image was used only for broad anatomy, proportion, and personality cues. It is not included in this repository.

## Contract and palette

The original standard-animation atlas is `1536 × 1872`, divided into `192 × 208` cells in an 8-column by 9-row layout:

1. `idle` — 6 mint-green frames
2. `running-right` — 8 aqua frames
3. `running-left` — 8 aqua frames
4. `waving` — 4 sunny-yellow frames
5. `jumping` — 5 coral-orange frames
6. `failed` — 8 soft-blue frames
7. `waiting` — 6 warm-amber frames
8. `running` — 6 teal focused-work frames
9. `review` — 6 lavender frames

The packaged v2 atlas preserves the standard six-frame idle row and the remaining standard-state counts, then adds two look-direction rows, producing an 8-column by 11-row `1536 × 2288` atlas. Row 9 contains `000` through `157.5`; row 10 contains `180` through `337.5`, in clockwise 22.5-degree steps. Unused atlas cells are fully transparent.

## Latest atlas refresh

On 2026-07-18, the packaged `kiko/spritesheet.webp` was replaced with the latest user-approved v2 atlas. The installable package is authoritative. Earlier generated strips, extracted frames, the 8×9 intermediate, GIFs, and manual-review records remain in `run/` as creation history rather than byte-for-byte rebuild inputs for the latest package.

During the final repository refresh, failed-state row 5 frame 4 was found translated about 6 pixels right and 14 pixels down, clipping its outer edge. The complete frame was restored at its prior registered position without changing the other cells, then the atlas and all current v2 QA artifacts were regenerated and reviewed again.

The current v2 contact sheet, direction sheet, and structural validation are regenerated directly from the packaged atlas with `scripts/update-v2-assets.py`. This keeps derived assets synchronized without rewriting the historical generation record.

## Manual finishing workflow

Automated image generation is useful for producing an initial character and motion draft, but it did not consistently meet the desired quality for Kiko's final animation. The generated rows are therefore treated as starting material rather than finished assets.

Each animation frame is reviewed and manually edited to refine Kiko's identity, expression, silhouette, color transition, transparency, motion cadence, and continuity with adjacent frames. Once the full atlas is satisfactory, the manually finished image replaces `kiko/spritesheet.webp`; that packaged WebP is the authoritative artwork.

After any manual atlas update, run:

```bash
python3 scripts/update-v2-assets.py
```

This validates the 8×11 contract and regenerates the contact sheet, look-direction sheet, and animated state GIFs from the approved WebP. It does not regenerate or overwrite the manually edited artwork.

## V2 look-direction upgrade

Kiko's v2 look family keeps both feet, pelvis, lower torso, and low tail anchored. The complete physical eyeballs lead the gaze, with restrained head yaw or pitch and a smoothly bending neck. The original warm brown-and-gold eye construction, green/turquoise body, cream belly, scale, and facial proportions remain consistent.

The first row-10 attempt failed blind left/right QA because its left-half poses still read screen-right. The second corrected the gaze but rotated the torso and flipped the tail across the row boundary. The accepted third attempt keeps the front-facing torso and tail registered while the eyes, snout, head, and neck turn screen-left.

The completed 16-pose loop passed cardinal-anchor review, three-reviewer blind direction validation, labeled per-direction semantic review, deterministic continuity review, final visual QA, and v2 atlas validation. The review evidence is preserved under `run/v2/qa/`.

## Visual generation workflow

The built-in Codex image-generation path created one canonical base and state-specific horizontal strips. Each generated row used two grounding images:

1. the matching layout guide for slot count and spacing
2. the accepted canonical Kiko base for identity

The accepted rightward strip was safe to mirror because Kiko has no text, logos, directional markings, asymmetric identity features, or directional lighting. The leftward row was therefore derived with the bundled framewise mirror helper, preserving frame order and cadence.

### Accepted and repaired rows

- `idle`: six-frame camouflage-fade and blink sequence
- `running-right`: regenerated after the first version crossed slot boundaries; the accepted replacement uses a smaller sprite and compact tail
- `running-left`: deterministically mirrored from the repaired rightward strip
- `waving`: accepted; four prop-free hand poses
- `jumping`: accepted; five-frame vertical hop with no floor effects
- `failed`: regenerated after the first result drifted through unrelated colors/actions
- `waiting`: regenerated after the first result introduced a question mark and heart sign
- `running`: one transport retry was followed by a visual repair to remove invented work props
- `review`: regenerated after the first result recapped unrelated state colors

Rejected visual outputs are retained in `run/rejected/`.

## Transparency cleanup

Generated strips used a flat magenta chroma background. A first hard-threshold extraction passed structural checks but left a thin magenta antialias fringe. The final cleanup used the installed image-generation helper with auto border sampling, a soft matte, despill, and one-pixel edge contraction:

```bash
python ~/.codex/skills/.system/imagegen/scripts/remove_chroma_key.py \
  --input run/decoded/idle.png \
  --out run/decoded-clean/idle.png \
  --auto-key border \
  --soft-matte \
  --transparent-threshold 12 \
  --opaque-threshold 220 \
  --despill \
  --edge-contract 1 \
  --force
```

The lavender review row is closer to magenta than the other palettes, so soft matting partially erased its body. That row instead used a palette-safe hard key plus despill:

```bash
python ~/.codex/skills/.system/imagegen/scripts/remove_chroma_key.py \
  --input run/decoded/review.png \
  --out run/decoded-clean/review.png \
  --auto-key border \
  --tolerance 60 \
  --despill \
  --edge-contract 1 \
  --force
```

## Deterministic assembly

The bundled `hatch-pet` helpers performed the original frame extraction, inspection, atlas composition, validation, contact-sheet creation, and GIF rendering. `scripts/rebuild-atlas.sh` captures those historical rebuild commands, while `scripts/update-v2-assets.py` validates the current package and regenerates its v2 QA sheets.

The packaged v2 validation result is:

```json
{
  "ok": true,
  "format": "WEBP",
  "mode": "RGBA",
  "width": 1536,
  "height": 2288,
  "columns": 8,
  "rows": 11,
  "sprite_version_number": 2,
  "transparent_rgb_residue_pixels": 0,
  "errors": [],
  "warnings": []
}
```

The latest package passes structural validation with no errors or warnings. Historical frame inspection and manual semantic-review records remain under `run/`; they should not be interpreted as a fresh independent review of later atlas replacements.

## Package

The installable package contains only:

```text
kiko/
  pet.json
  spritesheet.webp
```

`pet.json` sets `spriteVersionNumber` to `2`. Copy that directory to `~/.codex/pets/kiko` to install it locally.
