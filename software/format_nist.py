"""Pack a CSV bit column into a binary file for external test tools.

Author: Trishan Biswas
Created: 14 April 2026
Repository update: 16 October 2026

Formatting data does not validate its randomness. Read docs/validation.md
before interpreting any statistical-test output.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=PROJECT_ROOT / "data" / "ED-1" / "qrng_bits.csv")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "results" / "ED-1" / "nist" / "qrng_nist.bin")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = args.output.resolve()
    if output.exists() and not args.overwrite:
        raise SystemExit(f"Refusing to overwrite {output}; pass --overwrite to replace it")

    bits: list[int] = []
    with args.input.resolve().open(newline="", encoding="utf-8") as handle:
        for line_number, row in enumerate(csv.DictReader(handle), start=2):
            bit = int(row["bit"])
            if bit not in (0, 1):
                raise ValueError(f"Invalid bit at line {line_number}")
            bits.append(bit)

    bit_array = np.asarray(bits, dtype=np.uint8)
    packed = np.packbits(bit_array, bitorder="big")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(packed.tobytes())
    print(f"Wrote {len(packed):,} bytes for {len(bit_array):,} input bits")
    print(f"Final-byte padding: {(-len(bit_array)) % 8} zero bits")
    print(output)


if __name__ == "__main__":
    main()
