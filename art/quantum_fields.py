"""
quantum_fields.py -- Flow field driven by recorded hardware bits

Author: Trishan Biswas
Created: 14 April 2026
Repository update: 16 October 2026

Generates a vector field where the angle at each grid point comes from
recorded bits, then traces particle paths through the field.
The result visually resembles magnetic field lines or fluid flow.

Concept:
    A flow field assigns an angle to every point on a grid. Particles
    follow the flow like leaves on a river. This artwork is reproducible
    when supplied with the same saved bitstream.

Usage:
    python quantum_fields.py
"""

import math
import numpy as np
from PIL import Image, ImageDraw
from pathlib import Path

from qrng_source import QRNGSource
from palettes import CHERENKOV_BLUE

WIDTH = 4000
HEIGHT = 4000
CELL_SIZE = 40           # flow field grid resolution (bigger = fewer cells)
N_PARTICLES = 2000        # number of particle traces
STEPS_PER_PARTICLE = 150  # how far each particle walks
BG_COLOR = (5, 10, 30)

OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def make_flow_field(qrng, cols, rows):
    """Build a grid of angles from QRNG bits.

    Uses 10 bits per cell (1024 angle steps) instead of 32-bit random()
    to stay within the 1M bit budget.
    """
    field = np.zeros((cols, rows))
    for i in range(cols):
        for j in range(rows):
            field[i][j] = qrng.randint(0, 1023) / 1024.0 * 2 * math.pi
    return field


def get_angle(field, x, y, cols, rows):
    """Bilinear interpolation of the flow field at position (x, y)."""
    gx = x / CELL_SIZE
    gy = y / CELL_SIZE

    x0 = int(gx) % cols
    y0 = int(gy) % rows
    x1 = (x0 + 1) % cols
    y1 = (y0 + 1) % rows

    fx = gx - int(gx)
    fy = gy - int(gy)

    a00 = field[x0][y0]
    a10 = field[x1][y0]
    a01 = field[x0][y1]
    a11 = field[x1][y1]

    sx = (math.sin(a00) * (1 - fx) * (1 - fy) +
          math.sin(a10) * fx * (1 - fy) +
          math.sin(a01) * (1 - fx) * fy +
          math.sin(a11) * fx * fy)
    cx = (math.cos(a00) * (1 - fx) * (1 - fy) +
          math.cos(a10) * fx * (1 - fy) +
          math.cos(a01) * (1 - fx) * fy +
          math.cos(a11) * fx * fy)

    return math.atan2(sx, cx)


def draw_particle(draw, field, cols, rows, qrng, palette):
    """Trace one particle through the flow field and draw its path."""
    x = qrng.random() * WIDTH
    y = qrng.random() * HEIGHT
    color = qrng.choice(palette)
    r, g, b = color

    points = [(x, y)]
    for _ in range(STEPS_PER_PARTICLE):
        angle = get_angle(field, x, y, cols, rows)
        # 3-bit step size variation (1-8 pixels)
        step = qrng.randint(0, 7) + 1
        x += math.cos(angle) * step
        y += math.sin(angle) * step
        x = x % WIDTH
        y = y % HEIGHT
        points.append((x, y))

    for i in range(len(points) - 1):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        if abs(x1 - x0) > WIDTH / 2 or abs(y1 - y0) > HEIGHT / 2:
            continue
        alpha = int(60 + 140 * (1.0 - i / len(points)))
        draw.line([(x0, y0), (x1, y1)], fill=(r, g, b, alpha), width=2)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    qrng = QRNGSource()

    cols = WIDTH // CELL_SIZE
    rows = HEIGHT // CELL_SIZE

    print(f"Generating flow field ({cols}x{rows} grid)...")
    field = make_flow_field(qrng, cols, rows)
    field_bits = qrng.bits_consumed
    print(f"  Field generated. Bits used: {field_bits:,}  Remaining: {qrng.bits_remaining:,}")

    print(f"Creating canvas ({WIDTH}x{HEIGHT})...")
    img = Image.new("RGBA", (WIDTH, HEIGHT), BG_COLOR + (255,))
    draw = ImageDraw.Draw(img)

    # Per particle: 32 (x) + 32 (y) + 3 (choice) + 150 * 3 (step) = 517 bits
    # 2000 particles ~ 1.03M. With 2500 remaining bits after field, can do ~4-5
    # Need to recalc: field is 100*100 * 10 = 100,000 bits. Leaves 900,000.
    # 900,000 / 517 ~ 1740 particles. Let's do 1500 to be safe.
    actual_particles = min(N_PARTICLES, qrng.bits_remaining // 520)
    print(f"Tracing {actual_particles} particles through the field...")
    for i in range(actual_particles):
        draw_particle(draw, field, cols, rows, qrng, CHERENKOV_BLUE)
        if (i + 1) % 200 == 0:
            print(f"  {i + 1:>5}/{actual_particles} particles traced  "
                  f"({qrng.bits_remaining:,} bits left)")

    output_path = OUTPUT_DIR / "quantum_fields.png"
    rgb = Image.new("RGB", img.size, BG_COLOR)
    rgb.paste(img, mask=img.split()[3])
    rgb.save(output_path, dpi=(300, 300))
    print(f"\nSaved: {output_path}")
    print(f"Bits consumed: {qrng.bits_consumed:,}")


if __name__ == "__main__":
    main()
