"""
palettes.py -- Color palettes derived from quantum physics phenomena

Author: Trishan Biswas
Created: 14 April 2026
Repository update: 16 October 2026

Each palette is a list of (R, G, B) tuples. The names reference real
physical phenomena that produce these colours in nature.

CHERENKOV_BLUE:   The eerie blue glow of Cherenkov radiation in a
                   nuclear reactor core. Charged particles exceeding
                   the speed of light in water emit this characteristic
                   blue. It is often described as the electromagnetic
                   analogue of a sonic boom.

HYDROGEN_LINES:    The visible emission spectrum of hydrogen. When
                   electrons drop between energy levels, they emit
                   photons at very specific wavelengths: 410nm (violet),
                   434nm (blue-violet), 486nm (cyan), 656nm (red).

COSMIC_BACKGROUND: Colours inspired by the cosmic microwave background
                   radiation map. The tiny temperature fluctuations from
                   380,000 years after the Big Bang, rendered in the
                   classic WMAP colour scheme.

AURORA:            The green-red-purple of aurora borealis. Solar wind
                   particles excite nitrogen and oxygen in the upper
                   atmosphere, which then emit photons at characteristic
                   wavelengths as they relax.

SCHRODINGER:       A palette that sits between life and death. Warm ambers
                   and cold teals, representing the superposition of states
                   before the wavefunction collapses.

Usage:
    from palettes import CHERENKOV_BLUE
    from qrng_source import QRNGSource
    qrng = QRNGSource()
    color = qrng.choice(CHERENKOV_BLUE)
"""

CHERENKOV_BLUE = [
    (10, 20, 60),
    (20, 50, 120),
    (40, 100, 180),
    (80, 160, 220),
    (140, 200, 240),
    (200, 230, 255),
    (230, 245, 255),
    (10, 15, 40),
]

HYDROGEN_LINES = [
    (90, 0, 150),      # 410nm violet (H-delta)
    (120, 20, 180),    # 434nm blue-violet (H-gamma)
    (0, 160, 200),     # 486nm cyan (H-beta)
    (0, 180, 170),     # cyan-teal transition
    (220, 30, 30),     # 656nm red (H-alpha)
    (180, 15, 50),     # deep red
    (50, 5, 80),       # near-UV dark
    (0, 100, 130),     # mid cyan
]

COSMIC_BACKGROUND = [
    (15, 10, 50),
    (40, 20, 80),
    (80, 30, 100),
    (140, 50, 80),
    (200, 100, 50),
    (240, 180, 80),
    (255, 240, 200),
    (20, 15, 60),
]

AURORA = [
    (10, 40, 20),
    (20, 120, 50),
    (40, 200, 80),
    (100, 220, 100),
    (180, 50, 80),
    (200, 60, 150),
    (120, 30, 180),
    (15, 60, 30),
]

SCHRODINGER = [
    (240, 180, 50),    # warm amber (alive)
    (200, 140, 40),    # gold
    (160, 100, 30),    # dark amber
    (20, 140, 140),    # teal (dead)
    (30, 100, 120),    # dark teal
    (15, 60, 80),      # deep teal
    (60, 60, 60),      # neutral grey
    (200, 200, 180),   # bone white
]

ALL_PALETTES = {
    "cherenkov": CHERENKOV_BLUE,
    "hydrogen": HYDROGEN_LINES,
    "cosmic": COSMIC_BACKGROUND,
    "aurora": AURORA,
    "schrodinger": SCHRODINGER,
}
