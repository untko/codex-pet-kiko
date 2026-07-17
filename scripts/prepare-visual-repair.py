#!/usr/bin/env python3
"""Prepare Kiko's existing v2 atlas for a targeted visual repair."""

from __future__ import annotations

import argparse
import colorsys
import json
from pathlib import Path

from PIL import Image


CELL_WIDTH = 192
CELL_HEIGHT = 208
BASE_GREEN_HUE = 140.0
ROW_SPECS = [
    ("idle", 0, 6),
    ("running-right", 1, 8),
    ("running-left", 2, 8),
    ("waving", 3, 4),
    ("jumping", 4, 5),
    ("failed", 5, 8),
    ("waiting", 6, 6),
    ("running", 7, 6),
    ("review", 8, 6),
]
LOOK_LABELS = [
    "000",
    "022.5",
    "045",
    "067.5",
    "090",
    "112.5",
    "135",
    "157.5",
    "180",
    "202.5",
    "225",
    "247.5",
    "270",
    "292.5",
    "315",
    "337.5",
]

# Frame 0 stays fully visible for reduced-motion mode. The final frame returns
# to full opacity so the six-frame idle loop closes without a visibility jump.
IDLE_ALPHA = [1.0, 0.82, 0.55, 0.35, 0.65, 1.0]

# Preserve Kiko's distinct state palette, but enter and leave each color through
# green bookends or intermediate blends so repeated rows do not hard-cut from
# the default mint body to a saturated destination color.
COLOR_PLANS = {
    "waving": {
        "peak_hue": 44.0,
        "peak_saturation": 0.55,
        "envelope": [0.0, 0.55, 1.0, 0.55],
    },
    "jumping": {
        "peak_hue": 25.0,
        "peak_saturation": 0.58,
        "envelope": [0.0, 0.5, 1.0, 0.5, 0.0],
    },
    "failed": {
        "peak_hue": 205.0,
        "peak_saturation": 0.46,
        "envelope": [0.0, 0.33, 0.67, 1.0, 1.0, 0.67, 0.33, 0.0],
    },
    "waiting": {
        "peak_hue": 39.0,
        "peak_saturation": 0.52,
        "envelope": [0.0, 0.5, 1.0, 1.0, 0.5, 0.0],
    },
    "running": {
        "peak_hue": 155.0,
        "peak_saturation": 0.45,
        "envelope": [0.0, 0.5, 1.0, 1.0, 0.5, 0.0],
    },
    "review": {
        "peak_hue": 278.0,
        "peak_saturation": 0.38,
        "envelope": [0.0, 0.5, 1.0, 1.0, 0.5, 0.0],
    },
}


def circular_distance(left: float, right: float) -> float:
    return abs((left - right + 180.0) % 360.0 - 180.0)


def circular_lerp(start: float, end: float, amount: float) -> float:
    delta = (end - start + 180.0) % 360.0 - 180.0
    return (start + delta * amount) % 360.0


def hue_histogram(images: list[Image.Image]) -> list[float]:
    bins = [0.0] * 360
    for image in images:
        for red, green, blue, alpha in image.convert("RGBA").getdata():
            if alpha < 32:
                continue
            hue, saturation, value = colorsys.rgb_to_hsv(
                red / 255.0, green / 255.0, blue / 255.0
            )
            if saturation < 0.24 or value < 0.42:
                continue
            bins[int(round(hue * 359.0))] += saturation * value
    return bins


def dominant_hue(images: list[Image.Image]) -> float:
    bins = hue_histogram(images)
    smoothed = [
        sum(bins[(index + offset) % 360] for offset in range(-5, 6))
        for index in range(360)
    ]
    return float(max(range(360), key=smoothed.__getitem__))


def apply_alpha(image: Image.Image, multiplier: float) -> Image.Image:
    rgba = image.convert("RGBA")
    red, green, blue, alpha = rgba.split()
    alpha = alpha.point(lambda value: round(value * multiplier))
    return Image.merge("RGBA", (red, green, blue, alpha))


def recolor_body(
    image: Image.Image,
    source_hue: float,
    target_hue: float,
    target_saturation: float,
) -> Image.Image:
    rgba = image.convert("RGBA")
    output: list[tuple[int, int, int, int]] = []
    for index, (red, green, blue, alpha) in enumerate(rgba.getdata()):
        if alpha == 0:
            output.append((0, 0, 0, 0))
            continue
        hue, saturation, value = colorsys.rgb_to_hsv(
            red / 255.0, green / 255.0, blue / 255.0
        )
        hue_degrees = hue * 360.0
        is_body = (
            saturation >= 0.22
            and value >= 0.18
            and circular_distance(hue_degrees, source_hue) <= 48.0
        )
        is_gold_eye_detail = (
            index // rgba.width < round(rgba.height * 0.42)
            and
            (
                index % rgba.width < round(rgba.width * 0.45)
                or index % rgba.width > round(rgba.width * 0.55)
            )
            and
            15.0 <= hue_degrees <= 65.0
            and saturation >= 0.25
            and 0.38 <= value <= 0.82
        )
        # Preserve the pupil/iris construction and only the deepest skin
        # markings. Mid-tone limb shadows should follow the body hue, or they
        # read as orange flashes during state transitions.
        if not is_body or value < 0.18 or is_gold_eye_detail:
            output.append((red, green, blue, alpha))
            continue
        relative = (hue_degrees - source_hue + 180.0) % 360.0 - 180.0
        adjusted_hue = (target_hue + max(-16.0, min(16.0, relative)) * 0.32) % 360.0
        adjusted_saturation = max(
            0.0,
            min(1.0, saturation * 0.15 + target_saturation * 0.85),
        )
        out_red, out_green, out_blue = colorsys.hsv_to_rgb(
            adjusted_hue / 360.0, adjusted_saturation, value
        )
        output.append(
            (
                round(out_red * 255.0),
                round(out_green * 255.0),
                round(out_blue * 255.0),
                alpha,
            )
        )
    repaired = Image.new("RGBA", rgba.size)
    repaired.putdata(output)
    return repaired


def crop_cell(atlas: Image.Image, row: int, column: int) -> Image.Image:
    left = column * CELL_WIDTH
    top = row * CELL_HEIGHT
    return atlas.crop((left, top, left + CELL_WIDTH, top + CELL_HEIGHT)).convert("RGBA")


def save_clean(image: Image.Image, path: Path) -> None:
    data = bytearray(image.convert("RGBA").tobytes())
    for index in range(0, len(data), 4):
        if data[index + 3] == 0:
            data[index : index + 3] = b"\x00\x00\x00"
    cleaned = Image.frombytes("RGBA", image.size, bytes(data))
    path.parent.mkdir(parents=True, exist_ok=True)
    cleaned.save(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--atlas", required=True)
    parser.add_argument("--frames-root", required=True)
    parser.add_argument("--look-cells-dir", required=True)
    parser.add_argument("--neutral-cell", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    atlas_path = Path(args.atlas).expanduser().resolve()
    frames_root = Path(args.frames_root).expanduser().resolve()
    look_cells_dir = Path(args.look_cells_dir).expanduser().resolve()
    neutral_cell_path = Path(args.neutral_cell).expanduser().resolve()
    report_path = Path(args.report).expanduser().resolve()

    with Image.open(atlas_path) as opened:
        atlas = opened.convert("RGBA")
    if atlas.size != (1536, 2288):
        raise SystemExit(f"expected 1536x2288 v2 atlas, got {atlas.size}")

    source_rows: dict[str, list[Image.Image]] = {}
    for state, row, frame_count in ROW_SPECS:
        source_rows[state] = [crop_cell(atlas, row, column) for column in range(frame_count)]

    # The gold irises occupy enough of the idle cells to dominate a naive hue
    # histogram. Anchor to Kiko's approved mint body hue instead.
    base_hue = BASE_GREEN_HUE
    row_hues = {state: dominant_hue(images) for state, images in source_rows.items()}

    for state, _row, frame_count in ROW_SPECS:
        for column in range(frame_count):
            frame = source_rows[state][column]
            if state == "idle":
                frame = apply_alpha(frame, IDLE_ALPHA[column])
            elif state in COLOR_PLANS:
                plan = COLOR_PLANS[state]
                amount = plan["envelope"][column]
                target_hue = circular_lerp(base_hue, plan["peak_hue"], amount)
                base_saturation = 0.34
                target_saturation = (
                    base_saturation
                    + (plan["peak_saturation"] - base_saturation) * amount
                )
                frame = recolor_body(
                    frame,
                    row_hues[state],
                    target_hue,
                    target_saturation,
                )
            save_clean(frame, frames_root / state / f"{column:02d}.png")

    save_clean(crop_cell(atlas, 0, 6), neutral_cell_path)
    for index, label in enumerate(LOOK_LABELS):
        row = 9 + index // 8
        column = index % 8
        save_clean(crop_cell(atlas, row, column), look_cells_dir / f"{label}.png")

    report = {
        "ok": True,
        "source_atlas": str(atlas_path),
        "base_green_hue_degrees": round(base_hue, 2),
        "source_row_hues_degrees": {
            key: round(value, 2) for key, value in row_hues.items()
        },
        "idle_alpha_multipliers": IDLE_ALPHA,
        "color_plans": COLOR_PLANS,
        "notes": [
            "the preparation pass leaves running-right and running-left as placeholders; the final assembly replaces both with the approved repaired gait",
            "every recolored state enters from default green and exits through either green or an intermediate blend chosen for a smooth repeated loop",
            "neutral and all 16 approved v2 look cells are preserved from the source atlas",
        ],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
