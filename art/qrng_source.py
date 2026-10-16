"""
qrng_source.py: recorded hardware bitstream source for Bitstream Art

Author: Trishan Biswas
Created: 14 April 2026
Repository update: 16 October 2026

Reads the experimental entropy-source dataset from the hardware-qrng
project. The current LED/LM358/Arduino apparatus has not yet established
that its entropy is quantum in origin or suitable for cryptography.

If the bitstream runs out, QRNGExhausted is raised instead of silently
falling back to a pseudorandom-number generator.

Usage:
    from qrng_source import QRNGSource
    qrng = QRNGSource()
    x = qrng.random()           # float in [0, 1)
    n = qrng.randint(0, 255)    # int in [0, 255]
    c = qrng.choice(palette)    # random element from sequence
    g = qrng.gauss(0, 1)       # Gaussian using Box-Muller
"""

import csv
from pathlib import Path


class QRNGExhausted(Exception):
    """Raised when the QRNG bitstream has no more bits to give."""
    pass


class QRNGSource:
    """Random-like interface backed by a recorded hardware bitstream."""

    # Preserved ED-1 capture in this repository.
    QRNG_DATA = Path(__file__).resolve().parent.parent / "data" / "ED-1" / "qrng_bits.csv"

    def __init__(self):
        self._bits = []
        self._position = 0
        self._load()

    def _load(self):
        """Load the bitstream from CSV."""
        if not self.QRNG_DATA.exists():
            raise FileNotFoundError(
                f"QRNG data not found at {self.QRNG_DATA}. "
                f"Run the hardware QRNG collector first."
            )
        with open(self.QRNG_DATA, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None or "bit" not in reader.fieldnames:
                raise ValueError("Input CSV must contain a 'bit' column")
            for row in reader:
                bit = int(row["bit"])
                if bit not in (0, 1):
                    raise ValueError(f"Invalid bit value {bit!r}; expected 0 or 1")
                self._bits.append(bit)
        if not self._bits:
            raise ValueError("Input CSV contains no bits")
        print(f"QRNGSource: loaded {len(self._bits):,} recorded hardware bits")

    @property
    def bits_remaining(self):
        return len(self._bits) - self._position

    @property
    def bits_consumed(self):
        return self._position

    def _consume_bits(self, n):
        """Consume n bits from the stream and return as a list of 0/1."""
        if self._position + n > len(self._bits):
            raise QRNGExhausted(
                f"QRNG bitstream exhausted. Consumed {self._position:,} of "
                f"{len(self._bits):,} bits. Need {n} more."
            )
        bits = self._bits[self._position : self._position + n]
        self._position += n
        return bits

    def _bits_to_int(self, n_bits):
        """Consume n_bits bits and return as an unsigned integer."""
        bits = self._consume_bits(n_bits)
        value = 0
        for b in bits:
            value = (value << 1) | b
        return value

    def random(self):
        """Return a float in [0, 1) using 32 bits of QRNG data."""
        raw = self._bits_to_int(32)
        return raw / (2**32)

    def randint(self, a, b):
        """Return a random int in [a, b] using rejection sampling."""
        if a == b:
            return a
        span = b - a
        n_bits = span.bit_length()
        max_val = (1 << n_bits) - 1
        # Cutoff: largest multiple of (span+1) that fits in [0, max_val]
        cutoff = ((max_val + 1) // (span + 1)) * (span + 1)
        while True:
            val = self._bits_to_int(n_bits)
            if val < cutoff:
                return a + (val % (span + 1))

    def choice(self, seq):
        """Return a random element from a non-empty sequence."""
        if not seq:
            raise IndexError("Cannot choose from empty sequence")
        idx = self.randint(0, len(seq) - 1)
        return seq[idx]

    def gauss(self, mu=0.0, sigma=1.0):
        """Return a Gaussian random number using Box-Muller transform.

        Consumes 64 bits (two uniform floats).
        """
        import math
        while True:
            u1 = self.random()
            u2 = self.random()
            if u1 > 0:  # avoid log(0)
                break
        mag = sigma * math.sqrt(-2.0 * math.log(u1))
        z0 = mag * math.cos(2.0 * math.pi * u2)
        return mu + z0

    def shuffle(self, seq):
        """Shuffle a list in place using Fisher-Yates."""
        for i in range(len(seq) - 1, 0, -1):
            j = self.randint(0, i)
            seq[i], seq[j] = seq[j], seq[i]
