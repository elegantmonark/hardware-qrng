"""
quantum_mosaic.py -- Glowing mosaic driven by recorded hardware bits

Author: Trishan Biswas
Created: 14 April 2026
Repository update: 16 October 2026

A grid of tiles driven by recorded bits, each with colour, shape, depth,
and glow determined by the input bitstream. Tiles have 3D bevel
effects, glow halos, and varied shapes (squares, hexagons, diamonds,
circles). On a dark background, the glow makes them look like
illuminated quantum detector pixels.

Concept:
    The glow, energy-level and measurement language is an artistic
    metaphor. This program is not a simulation of quantum measurement.

Usage:
    python quantum_mosaic.py
"""

import math
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path

from qrng_source import QRNGSource
from palettes import CHERENKOV_BLUE, HYDROGEN_LINES, COSMIC_BACKGROUND

WIDTH = 4000
HEIGHT = 4000
TILE_SIZE = 60
GAP = 3
BG_COLOR = (3, 3, 8)

OUTPUT_DIR = Path(__file__).resolve().parent / "output"

# Tile shape types
SQUARE = 0
DIAMOND = 1
HEXAGON = 2
CIRCLE = 3


def brighten(color, factor):
    """Brighten an RGB colour by a factor (0.0 to 2.0+)."""
    r, g, b = color
    r = min(255, int(r * factor))
    g = min(255, int(g * factor))
    b = min(255, int(b * factor))
    return (r, g, b)


def lerp_color(c1, c2, t):
    """Linear interpolate between two colours. t in [0, 1]."""
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def get_tile_shape(qrng):
    """QRNG decides the tile shape."""
    val = qrng.randint(0, 3)
    return val


def hexagon_points(cx, cy, radius, angle_offset=0):
    """Return 6 vertices of a hexagon."""
    pts = []
    for i in range(6):
        a = math.radians(60 * i + angle_offset)
        pts.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
    return pts


def diamond_points(cx, cy, half_w, half_h):
    """Return 4 vertices of a diamond."""
    return [
        (cx, cy - half_h),
        (cx + half_w, cy),
        (cx, cy + half_h),
        (cx - half_w, cy),
    ]


def draw_glow(draw, cx, cy, color, radius, intensity):
    """Draw a radial glow around a point. Multiple translucent circles."""
    r, g, b = color
    for i in range(5):
        glow_r = radius + i * int(radius * 0.4)
        alpha = max(2, int(intensity * (1.0 - i / 5)))
        draw.ellipse(
            [cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r],
            fill=(r, g, b, alpha),
        )


def draw_beveled_tile(draw, corners, base_color, depth):
    """Draw a tile with a 3D bevel effect.

    depth > 0 means the tile is raised (bright top-left, dark bottom-right).
    depth < 0 means the tile is sunken.
    """
    # Base fill
    r, g, b = base_color
    draw.polygon(corners, fill=(r, g, b))

    # Highlight edge (top-left sides)
    if depth > 0:
        highlight = brighten(base_color, 1.4)
        shadow = brighten(base_color, 0.5)
    else:
        highlight = brighten(base_color, 0.6)
        shadow = brighten(base_color, 1.3)

    n = len(corners)
    # Draw highlight lines on first half of edges
    for i in range(n // 2):
        p1 = corners[i]
        p2 = corners[(i + 1) % n]
        draw.line([p1, p2], fill=highlight, width=max(1, abs(depth)))

    # Draw shadow lines on second half of edges
    for i in range(n // 2, n):
        p1 = corners[i]
        p2 = corners[(i + 1) % n]
        draw.line([p1, p2], fill=shadow, width=max(1, abs(depth)))


def draw_tile(draw, glow_layer, qrng, palette, cx, cy):
    """Draw one tile with glow, bevel, and shape variation."""
    shape = get_tile_shape(qrng)
    half = TILE_SIZE // 2

    # Small offset from grid
    ox = qrng.randint(0, 7) - 4
    oy = qrng.randint(0, 7) - 4
    x = cx + ox
    y = cy + oy

    # Rotation: 3 bits, -15 to +15 degrees
    angle = (qrng.randint(0, 7) - 4) * 3.75
    cos_a = math.cos(math.radians(angle))
    sin_a = math.sin(math.radians(angle))

    # Colour from palette
    color_idx = qrng.randint(0, len(palette) - 1)
    base_color = palette[color_idx]

    # Energy level: determines brightness and glow intensity
    energy = qrng.randint(0, 7)  # 0-7

    # Brightness based on energy
    bright = 0.6 + energy / 7.0 * 0.8
    tile_color = brighten(base_color, bright)

    # Depth for bevel: 3 bits
    depth = qrng.randint(0, 3) - 1  # -1, 0, 1, 2

    # Build corners based on shape
    if shape == SQUARE:
        corners = [(-half, -half), (half, -half), (half, half), (-half, half)]
        rotated = [
            (px * cos_a - py * sin_a + x, px * sin_a + py * cos_a + y)
            for px, py in corners
        ]
        draw_beveled_tile(draw, rotated, tile_color, depth)

    elif shape == DIAMOND:
        half_w = half
        half_h = half + qrng.randint(0, 7) - 4
        pts = diamond_points(x, y, half_w, half_h)
        # Rotate
        rotated = [
            ((px - x) * cos_a - (py - y) * sin_a + x,
             (px - x) * sin_a + (py - y) * cos_a + y)
            for px, py in pts
        ]
        draw_beveled_tile(draw, rotated, tile_color, depth)

    elif shape == HEXAGON:
        rad = half
        pts = hexagon_points(x, y, rad, angle_offset=30)
        draw_beveled_tile(draw, pts, tile_color, depth)

    elif shape == CIRCLE:
        r = half - qrng.randint(0, 3)
        draw.ellipse(
            [x - r, y - r, x + r, y + r],
            fill=tile_color,
        )
        # Inner ring for depth effect
        if depth > 0:
            inner_r = r - 3
            highlight = brighten(tile_color, 1.3)
            draw.ellipse(
                [x - inner_r, y - inner_r, x + inner_r, y + inner_r],
                outline=highlight, width=2,
            )

    # Glow effect on separate layer
    if energy >= 3:
        glow_color = brighten(base_color, 1.6)
        glow_intensity = int(30 + energy * 10)
        draw_glow(glow_layer, x, y, glow_color, half, glow_intensity)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    qrng = QRNGSource()

    cols = WIDTH // (TILE_SIZE + GAP)
    rows = HEIGHT // (TILE_SIZE + GAP)

    print(f"Creating canvas ({WIDTH}x{HEIGHT})...")
    print(f"Grid: {cols}x{rows} = {cols * rows} tiles")

    # Main tile layer
    img = Image.new("RGBA", (WIDTH, HEIGHT), BG_COLOR + (255,))
    draw = ImageDraw.Draw(img)

    # Glow layer (blurred later and composited)
    glow_img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_img)

    # Mix two palettes for variety
    palette = CHERENKOV_BLUE + HYDROGEN_LINES

    n_total = cols * rows
    count = 0
    print(f"Placing {n_total} bitstream-driven tiles...")
    for col in range(cols):
        for row in range(rows):
            cx = col * (TILE_SIZE + GAP) + TILE_SIZE // 2
            cy = row * (TILE_SIZE + GAP) + TILE_SIZE // 2
            draw_tile(draw, glow_draw, qrng, palette, cx, cy)
            count += 1
            if count % 500 == 0:
                print(f"  {count:>6}/{n_total} tiles placed  "
                      f"({qrng.bits_remaining:,} bits left)")

    # Blur the glow layer for soft bloom effect
    print("Applying glow bloom...")
    glow_blurred = glow_img.filter(ImageFilter.GaussianBlur(radius=20))

    # Composite: glow goes behind the tiles
    print("Compositing layers...")
    final = Image.new("RGBA", (WIDTH, HEIGHT), BG_COLOR + (255,))
    final = Image.alpha_composite(final, glow_blurred)
    final = Image.alpha_composite(final, img)

    # Add a second, wider bloom pass for extra glow
    glow_wide = glow_img.filter(ImageFilter.GaussianBlur(radius=60))
    # Blend at low opacity for subtle ambient glow
    glow_wide_low = glow_wide.point(lambda p: p // 3)
    final = Image.alpha_composite(final, glow_wide_low)

    output_path = OUTPUT_DIR / "quantum_mosaic.png"
    rgb = Image.new("RGB", final.size, BG_COLOR)
    rgb.paste(final, mask=final.split()[3])
    rgb.save(output_path, dpi=(300, 300))
    print(f"\nSaved: {output_path}")
    print(f"Bits consumed: {qrng.bits_consumed:,}")


if __name__ == "__main__":
    main()
