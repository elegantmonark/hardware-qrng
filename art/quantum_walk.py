"""
quantum_walk.py -- Random-walk visualization driven by recorded hardware bits

Author: Trishan Biswas
Created: 14 April 2026
Repository update: 16 October 2026

Runs hundreds of walkers where each step direction comes from the recorded
bitstream. Trails fade over time and visually recall particle tracks.

Concept:
    In a bubble chamber, charged particles leave trails as they pass
    through superheated liquid. Each trail records the particle's path
    through space, curved by magnetic fields. Here, the bubble-chamber and
    probability-amplitude language is an artistic metaphor. The program is
    not a particle-physics simulation.

Usage:
    python quantum_walk.py
"""

import math
from PIL import Image, ImageDraw
from pathlib import Path

from qrng_source import QRNGSource
from palettes import AURORA

WIDTH = 4000
HEIGHT = 4000
N_WALKERS = 300
STEPS_PER_WALKER = 200
STEP_SIZE = 5.0
BG_COLOR = (5, 5, 10)

OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def draw_walker(draw, qrng, palette):
    """Trace one random walker and draw its fading trail."""
    x = WIDTH / 2 + (qrng.random() - 0.5) * WIDTH * 0.6
    y = HEIGHT / 2 + (qrng.random() - 0.5) * HEIGHT * 0.6

    r, g, b = qrng.choice(palette)
    angle = qrng.random() * 2 * math.pi

    prev_x, prev_y = x, y
    for step in range(STEPS_PER_WALKER):
        # 5-bit turn: 32 values, -0.4 to +0.4 radians
        turn = (qrng.randint(0, 31) - 16) / 16.0 * 0.4
        angle += turn

        # 2-bit step length variation
        step_extra = qrng.randint(0, 3)
        step_len = STEP_SIZE + step_extra

        x += math.cos(angle) * step_len
        y += math.sin(angle) * step_len

        progress = step / STEPS_PER_WALKER
        alpha = int(200 * (1.0 - progress * 0.8))
        alpha = max(alpha, 10)
        lw = max(1, int(3 * (1.0 - progress * 0.7)))

        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            draw.line(
                [(prev_x, prev_y), (x, y)],
                fill=(r, g, b, alpha),
                width=lw,
            )

        prev_x, prev_y = x, y


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    qrng = QRNGSource()

    print(f"Creating canvas ({WIDTH}x{HEIGHT})...")
    img = Image.new("RGBA", (WIDTH, HEIGHT), BG_COLOR + (255,))
    draw = ImageDraw.Draw(img)

    # Rough bit budget: 32 (start pos) + 32 (start pos) + 3 (choice) + 32 (angle)
    # + 200 * (5 + 2) = 1407 per walker. 300 walkers ~ 422,100 bits. Fits.
    print(f"Running {N_WALKERS} bitstream-driven walkers "
          f"({STEPS_PER_WALKER} steps each)...")
    for i in range(N_WALKERS):
        draw_walker(draw, qrng, AURORA)
        if (i + 1) % 30 == 0:
            print(f"  {i + 1:>4}/{N_WALKERS} walkers traced  "
                  f"({qrng.bits_remaining:,} bits left)")

    output_path = OUTPUT_DIR / "quantum_walk.png"
    rgb = Image.new("RGB", img.size, BG_COLOR)
    rgb.paste(img, mask=img.split()[3])
    rgb.save(output_path, dpi=(300, 300))
    print(f"\nSaved: {output_path}")
    print(f"Bits consumed: {qrng.bits_consumed:,}")


if __name__ == "__main__":
    main()
