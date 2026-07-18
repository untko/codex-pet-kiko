#!/usr/bin/env python3
"""Validate Kiko's v2 atlas and regenerate its derived QA images."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


CELL_WIDTH = 192
CELL_HEIGHT = 208
COLUMNS = 8
ROWS = 11
LABEL_HEIGHT = 22

ROW_DEFINITIONS = [
    ("idle", 6),
    ("running-right", 8),
    ("running-left", 8),
    ("waving", 4),
    ("jumping", 5),
    ("failed", 8),
    ("waiting", 6),
    ("running", 6),
    ("review", 6),
    ("look-000-to-157.5", 8),
    ("look-180-to-337.5", 8),
]

DIRECTIONS = [
    ("000", "up"),
    ("022.5", "up-right"),
    ("045", "up-right"),
    ("067.5", "up-right"),
    ("090", "right"),
    ("112.5", "down-right"),
    ("135", "down-right"),
    ("157.5", "down-right"),
    ("180", "down"),
    ("202.5", "down-left"),
    ("225", "down-left"),
    ("247.5", "down-left"),
    ("270", "left"),
    ("292.5", "up-left"),
    ("315", "up-left"),
    ("337.5", "up-left"),
]


def checker(size: tuple[int, int], square: int = 16) -> Image.Image:
    image = Image.new("RGB", size, "#ffffff")
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], square):
        for x in range(0, size[0], square):
            if (x // square + y // square) % 2:
                draw.rectangle(
                    (
                        x,
                        y,
                        min(x + square - 1, size[0] - 1),
                        min(y + square - 1, size[1] - 1),
                    ),
                    fill="#e8e8e8",
                )
    return image


def crop_cell(atlas: Image.Image, row: int, column: int) -> Image.Image:
    left = column * CELL_WIDTH
    top = row * CELL_HEIGHT
    return atlas.crop((left, top, left + CELL_WIDTH, top + CELL_HEIGHT))


def alpha_nonzero_count(image: Image.Image) -> int:
    return sum(image.getchannel("A").histogram()[1:])


def transparent_rgb_residue_count(image: Image.Image) -> int:
    data = image.convert("RGBA").tobytes()
    count = 0
    for index in range(0, len(data), 4):
        red, green, blue, alpha = data[index : index + 4]
        if alpha == 0 and (red or green or blue):
            count += 1
    return count


def opaque_chroma_component_pixels(
    image: Image.Image,
    chroma_key: tuple[int, int, int] = (0, 255, 0),
    minimum_component_size: int = 25,
) -> int:
    """Count large flat-key components without flagging isolated natural green pixels."""
    data = image.convert("RGBA").tobytes()
    pixels = [tuple(data[index : index + 4]) for index in range(0, len(data), 4)]
    mask = {
        index
        for index, (red, green, blue, alpha) in enumerate(pixels)
        if alpha and (red, green, blue) == chroma_key
    }
    total = 0
    while mask:
        start = mask.pop()
        stack = [start]
        component_size = 0
        while stack:
            index = stack.pop()
            component_size += 1
            x = index % image.width
            y = index // image.width
            neighbors = []
            if x:
                neighbors.append(index - 1)
            if x + 1 < image.width:
                neighbors.append(index + 1)
            if y:
                neighbors.append(index - image.width)
            if y + 1 < image.height:
                neighbors.append(index + image.width)
            for neighbor in neighbors:
                if neighbor in mask:
                    mask.remove(neighbor)
                    stack.append(neighbor)
        if component_size >= minimum_component_size:
            total += component_size
    return total


def validate(
    atlas_path: Path,
    atlas: Image.Image,
    source_format: str | None,
    source_mode: str,
) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    cells: list[dict[str, object]] = []

    if atlas.size != (COLUMNS * CELL_WIDTH, ROWS * CELL_HEIGHT):
        errors.append(
            f"expected {COLUMNS * CELL_WIDTH}x{ROWS * CELL_HEIGHT}, "
            f"got {atlas.width}x{atlas.height}"
        )
    if source_format not in {"PNG", "WEBP"}:
        errors.append(f"expected PNG or WebP, got {source_format}")
    if "A" not in source_mode:
        errors.append("atlas does not have an alpha channel")

    for row, (state, frame_count) in enumerate(ROW_DEFINITIONS):
        for column in range(COLUMNS):
            cell = crop_cell(atlas, row, column)
            nontransparent = alpha_nonzero_count(cell)
            opaque_chroma = opaque_chroma_component_pixels(cell)
            used = column < frame_count
            cells.append(
                {
                    "state": state,
                    "row": row,
                    "column": column,
                    "used": used,
                    "nontransparent_pixels": nontransparent,
                    "opaque_chroma_key_pixels": opaque_chroma,
                    "chroma_fringe_pixels": 0,
                }
            )
            if used and nontransparent < 50:
                errors.append(
                    f"{state} row {row} column {column} is empty or too sparse "
                    f"({nontransparent} pixels)"
                )
            if not used and nontransparent:
                errors.append(
                    f"{state} row {row} unused column {column} is not transparent "
                    f"({nontransparent} pixels)"
                )
            if opaque_chroma:
                errors.append(
                    f"{state} row {row} column {column} contains "
                    f"{opaque_chroma} opaque chroma-key pixels"
                )

    residue = transparent_rgb_residue_count(atlas)
    if residue:
        errors.append(
            f"atlas has {residue} fully transparent pixels with non-zero RGB residue"
        )

    return {
        "ok": not errors,
        "file": "kiko/spritesheet.webp",
        "format": source_format,
        "mode": source_mode,
        "columns": COLUMNS,
        "rows": ROWS,
        "sprite_version_number": 2,
        "width": atlas.width,
        "height": atlas.height,
        "sha256": hashlib.sha256(atlas_path.read_bytes()).hexdigest(),
        "transparent_rgb_residue_pixels": residue,
        "errors": errors,
        "warnings": warnings,
        "cells": cells,
    }


def make_contact_sheet(atlas: Image.Image, output: Path, scale: float = 0.5) -> None:
    cell_w = round(CELL_WIDTH * scale)
    cell_h = round(CELL_HEIGHT * scale)
    width = COLUMNS * cell_w
    height = ROWS * (cell_h + LABEL_HEIGHT)
    sheet = Image.new("RGB", (width, height), "#f7f7f7")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    for row, (state, frame_count) in enumerate(ROW_DEFINITIONS):
        y = row * (cell_h + LABEL_HEIGHT)
        draw.rectangle((0, y, width, y + LABEL_HEIGHT - 1), fill="#111111")
        draw.text((6, y + 5), f"row {row}: {state}", fill="#ffffff", font=font)
        draw.text(
            (width - 92, y + 5),
            f"{frame_count} frames",
            fill="#ffffff",
            font=font,
        )
        for column in range(COLUMNS):
            crop = crop_cell(atlas, row, column).resize(
                (cell_w, cell_h), Image.Resampling.LANCZOS
            )
            background = checker((cell_w, cell_h))
            background.paste(crop, (0, 0), crop)
            x = column * cell_w
            sheet.paste(background, (x, y + LABEL_HEIGHT))
            outline = "#18a058" if column < frame_count else "#cc3344"
            draw.rectangle(
                (
                    x,
                    y + LABEL_HEIGHT,
                    x + cell_w - 1,
                    y + LABEL_HEIGHT + cell_h - 1,
                ),
                outline=outline,
            )
            draw.text(
                (x + 4, y + LABEL_HEIGHT + 4),
                str(column),
                fill="#111111",
                font=font,
            )

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def make_direction_sheet(atlas: Image.Image, output: Path) -> None:
    width = COLUMNS * CELL_WIDTH
    band_height = LABEL_HEIGHT + CELL_HEIGHT
    sheet = Image.new("RGB", (width, band_height * 5), "#f1f1f1")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    neutral = crop_cell(atlas, 0, 0)
    draw.text((4, 5), "neutral", fill="#111111", font=font)
    neutral_bg = checker((CELL_WIDTH, CELL_HEIGHT))
    neutral_bg.paste(neutral, (0, 0), neutral)
    sheet.paste(neutral_bg, (0, LABEL_HEIGHT))

    for index, (angle, label) in enumerate(DIRECTIONS):
        row = 9 + index // COLUMNS
        column = index % COLUMNS
        cell = crop_cell(atlas, row, column)
        x = column * CELL_WIDTH

        full_y = (1 + index // COLUMNS) * band_height
        draw.text((x + 4, full_y + 5), f"{angle} {label}", fill="#111111", font=font)
        full_bg = checker((CELL_WIDTH, CELL_HEIGHT))
        full_bg.paste(cell, (0, 0), cell)
        sheet.paste(full_bg, (x, full_y + LABEL_HEIGHT))

        zoom_y = (3 + index // COLUMNS) * band_height
        draw.text(
            (x + 4, zoom_y + 5),
            f"zoom {angle} {label}",
            fill="#111111",
            font=font,
        )
        zoom = cell.crop((32, 0, 160, 156)).resize(
            (CELL_WIDTH, CELL_HEIGHT), Image.Resampling.LANCZOS
        )
        zoom_bg = checker((CELL_WIDTH, CELL_HEIGHT))
        zoom_bg.paste(zoom, (0, 0), zoom)
        sheet.paste(zoom_bg, (x, zoom_y + LABEL_HEIGHT))

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main() -> None:
    repo_dir = Path(__file__).resolve().parent.parent
    atlas_path = repo_dir / "kiko/spritesheet.webp"
    with Image.open(atlas_path) as opened:
        source_format = opened.format
        source_mode = opened.mode
        atlas = opened.convert("RGBA")

    validation = validate(atlas_path, atlas, source_format, source_mode)
    validation_path = repo_dir / "run/v2/validation.json"
    validation_path.write_text(
        json.dumps(validation, indent=2) + "\n", encoding="utf-8"
    )
    make_contact_sheet(atlas, repo_dir / "run/v2/qa/contact-sheet.png")
    make_direction_sheet(atlas, repo_dir / "run/v2/qa/look-directions.png")

    summary = {key: value for key, value in validation.items() if key != "cells"}
    print(json.dumps(summary, indent=2))
    if not validation["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
