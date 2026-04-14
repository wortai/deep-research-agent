#!/usr/bin/env python3
"""
Renders WORT dot-matrix letter patterns to a PNG for visual verification.
Usage: python3 wort_pattern_viz.py
Outputs: wort_preview.png
"""

from PIL import Image, ImageDraw

# ── Configuration ──
DOT_SIZE = 18  # px per dot
DOT_GAP = 4  # px gap between dots
CELL = DOT_SIZE + DOT_GAP
BG_COLOR = (20, 20, 20)
DOT_COLOR = (52, 211, 153)  # emerald-400 (#34d399)
DOT_OFF_COLOR = (40, 40, 40)  # dim dots for empty cells
LETTER_GAP = 2  # columns between letters
PADDING = 40  # px padding around grid
FONT_SIZE_RATIO = 0.55  # for labeling

# ── Define letter patterns ──
# Each letter is a list of (row, col) positions.  Row 0 = top.


def get_w_positions():
    """W: two outer legs + two inner V legs that cross at the middle."""
    pos = []
    # Outer legs (cols 0 and 7) — full height
    for r in range(0, 8):
        pos.append((r, 0))
        pos.append((r, 7))
    # Left inner V (cols 3,4) — comes down then back up
    pos.extend([(3, 3), (4, 3), (5, 3), (6, 3)])
    pos.extend([(4, 4)])
    # Right inner V (cols 4,5) — mirrors the left
    pos.extend([(4, 5)])
    pos.extend([(3, 6), (4, 6), (5, 6), (6, 6)])
    # Crossbar at row 4
    pos.extend([(4, 1), (4, 2)])
    return pos


def get_o_positions():
    """O: hollow rectangle with 2-dot-thick walls."""
    pos = []
    # Top/bottom bars (3 dots thick)
    for c in range(2, 6):
        pos.append((0, c))
        pos.append((7, c))
    # Side walls (2-dot thick, rows 1-6)
    for r in range(1, 7):
        pos.append((r, 1))
        pos.append((r, 2))
        pos.append((r, 5))
        pos.append((r, 6))
    return pos


def get_r_positions():
    """R: vertical left edge + P bowl + diagonal leg."""
    pos = []
    # Left edge (full height)
    for r in range(0, 8):
        pos.append((r, 0))
        pos.append((r, 1))
    # Top bar
    for c in range(2, 5):
        pos.append((0, c))
    # Right wall of bowl (rows 1-3)
    for r in range(1, 4):
        pos.append((r, 5))
        pos.append((r, 6))
    # Middle bar (row 4)
    for c in range(2, 5):
        pos.append((4, c))
    # Diagonal leg (rows 5-7)
    pos.extend([(5, 4), (6, 5), (7, 6)])
    return pos


def get_t_positions():
    """T: wide horizontal top + 2-wide vertical stem."""
    pos = []
    # Top bar
    for c in range(0, 7):
        pos.append((0, c))
    # Stem (centered, cols 2-3)
    for r in range(1, 8):
        pos.append((r, 2))
        pos.append((r, 3))
    return pos


# ── Build layout ──
letters = [
    ("W", get_w_positions()),
    ("O", get_o_positions()),
    ("R", get_r_positions()),
    ("T", get_t_positions()),
]

# Calculate column offsets for each letter
col_offsets = []
current_col = 0
for name, positions in letters:
    col_offsets.append(current_col)
    max_col = max(c for _, c in positions)
    current_col += max_col + 1 + LETTER_GAP  # +1 for 0-indexed, +LETTER_GAP for spacing

total_cols = current_col - LETTER_GAP  # remove trailing gap
total_rows = max(r for _, positions in letters for r, _ in positions) + 1

print(f"Grid: {total_cols} cols × {total_rows} rows")
print(f"Total dots: {sum(len(p) for _, p in letters)}")
for name, positions in letters:
    print(f"  {name}: {len(positions)} dots")

# ── Render to image ──
img_w = PADDING * 2 + total_cols * CELL
img_h = PADDING * 2 + total_rows * CELL
img = Image.new("RGB", (img_w, img_h), BG_COLOR)
draw = ImageDraw.Draw(img)

# Draw grid dots
for letter_idx, (name, positions) in enumerate(letters):
    offset = col_offsets[letter_idx]
    for r, c in positions:
        x = PADDING + (c + offset) * CELL
        y = PADDING + r * CELL
        draw.ellipse(
            [x, y, x + DOT_SIZE - 1, y + DOT_SIZE - 1],
            fill=DOT_COLOR,
        )

# Also draw faint dots for empty cells (to see the grid)
all_occupied = set()
for letter_idx, (name, positions) in enumerate(letters):
    offset = col_offsets[letter_idx]
    for r, c in positions:
        all_occupied.add((r, c + offset))

for r in range(total_rows):
    for c in range(total_cols):
        if (r, c) not in all_occupied:
            x = PADDING + c * CELL
            y = PADDING + r * CELL
            draw.ellipse(
                [x, y, x + DOT_SIZE - 1, y + DOT_SIZE - 1],
                fill=DOT_OFF_COLOR,
            )

# Label each letter
for letter_idx, (name, positions) in enumerate(letters):
    offset = col_offsets[letter_idx]
    min_c = min(c for _, c in positions) + offset
    max_c = max(c for _, c in positions) + offset
    center_c = (min_c + max_c) / 2
    label_x = PADDING + center_c * CELL
    label_y = PADDING + total_rows * CELL + 10
    # Simple label using text
    try:
        from PIL import ImageFont

        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), name, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((label_x - tw / 2, label_y), name, fill=(150, 150, 150), font=font)

# Grid info
info = f"{total_cols}×{total_rows} grid | {sum(len(p) for _, p in letters)} dots"
try:
    from PIL import ImageFont

    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
except:
    font = ImageFont.load_default()
draw.text((PADDING, 5), info, fill=(100, 100, 100), font=font)

# Save
out_path = "/Users/choclate/Desktop/WORT/wort_preview.png"
img.save(out_path)
print(f"\nSaved to {out_path}")
