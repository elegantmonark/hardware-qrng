"""
quantum_circles.py -- Circle composition driven by recorded hardware bits

Author: Trishan Biswas
Created: 14 April 2026
Repository update: 16 October 2026

Places circles at bitstream-determined positions with bitstream-determined
radii and colours. Dense, overlapping, translucent circles fill the canvas.

Concept:
    The circles use measurement and superposition as visual metaphors.
    The program is not a physical simulation of either process.

Usage:
    python quantum_circles.py
"""

from PIL import Image, ImageDraw
from pathlib import Path

from qrng_source import QRNGSource
from palettes import HYDROGEN_LINES

WIDTH = 4000
HEIGHT = 4000
N_CIRCLES = 3000
MIN_RADIUS = 10
MAX_RADIUS = 200
BG_COLOR = (8, 5, 15)

OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def draw_circle(draw, qrng, palette):
    """Draw one QRNG-driven circle."""
    x = qrng.random() * WIDTH
    y = qrng.random() * HEIGHT
    radius = qrng.randint(MIN_RADIUS, MAX_RADIUS)
    red, green, blue = qrng.choice(palette)
    alpha = qrng.randint(40, 160)

    # Draw on an overlay for alpha blending
    bbox = [x - radius, y - radius, x + radius, y + radius]
    draw.ellipse(bbox, fill=(red, green, blue, alpha))


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    qrng = QRNGSource()

    print(f"Creating canvas ({WIDTH}x{HEIGHT})...")
    img = Image.new("RGBA", (WIDTH, HEIGHT), BG_COLOR + (255,))
    draw = ImageDraw.Draw(img)

    print(f"Drawing {N_CIRCLES} bitstream-driven circles...")
    for i in range(N_CIRCLES):
        draw_circle(draw, qrng, HYDROGEN_LINES)
        if (i + 1) % 500 == 0:
            print(f"  {i + 1:>5}/{N_CIRCLES} circles drawn  "
                  f"({qrng.bits_remaining:,} bits left)")

    output_path = OUTPUT_DIR / "quantum_circles.png"
    rgb = Image.new("RGB", img.size, BG_COLOR)
    rgb.paste(img, mask=img.split()[3])
    rgb.save(output_path, dpi=(300, 300))
    print(f"\nSaved: {output_path}")
    print(f"Bits consumed: {qrng.bits_consumed:,}")


if __name__ == "__main__":
    main()
