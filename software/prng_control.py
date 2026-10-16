"""Generate a reproducible Mersenne Twister control sequence.

Author: Trishan Biswas
Created: 14 April 2026
Repository update: 16 October 2026

The control is deterministic and is included to catch plotting/analysis bugs,
not as a physical or security benchmark.
"""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20260413)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "data" / "controls" / "prng_bits.csv")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = args.output.resolve()
    if output.exists() and not args.overwrite:
        raise SystemExit(f"Refusing to overwrite {output}; pass --overwrite to replace it")
    if args.samples < 1:
        raise SystemExit("--samples must be positive")

    generator = random.Random(args.seed)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["raw", "bit"])
        for _ in range(args.samples):
            bit = generator.getrandbits(1)
            writer.writerow([bit, bit])
    print(f"Saved {args.samples:,} deterministic control bits with seed {args.seed} to {output}")


if __name__ == "__main__":
    main()
