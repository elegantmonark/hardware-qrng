"""Apply an educational debiaser to a captured bitstream.

Author: Trishan Biswas
Created: 24 September 2026
Repository update: 16 October 2026

The von Neumann rule maps 01 -> 0 and 10 -> 1, while discarding 00 and 11.
Its usual unbiased-output argument assumes independent input samples with a
stable bias. Those assumptions have not been established for this prototype,
so this tool does not produce cryptographically certified randomness.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=PROJECT_ROOT / "data" / "ED-1" / "qrng_bits.csv")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "data" / "ED-1" / "derived" / "april_2026_von_neumann.bin")
    parser.add_argument("--method", choices=["von-neumann"], default="von-neumann")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def load_bits(path: Path) -> np.ndarray:
    bits: list[int] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for line_number, row in enumerate(reader, start=2):
            bit = int(row["bit"])
            if bit not in (0, 1):
                raise ValueError(f"Invalid bit at line {line_number}")
            bits.append(bit)
    return np.asarray(bits, dtype=np.uint8)


def von_neumann(bits: np.ndarray) -> np.ndarray:
    pairs = bits[: len(bits) - (len(bits) % 2)].reshape(-1, 2)
    keep = pairs[:, 0] != pairs[:, 1]
    return pairs[keep, 0]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    args = parse_args()
    input_path = args.input.resolve()
    output_path = args.output.resolve()
    if output_path.exists() and not args.overwrite:
        raise SystemExit(f"Refusing to overwrite {output_path}; pass --overwrite to replace it")

    input_bits = load_bits(input_path)
    output_bits = von_neumann(input_bits)
    packed = np.packbits(output_bits, bitorder="big")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(packed.tobytes())
    metadata = {
        "method": "von-neumann",
        "mapping": {"01": 0, "10": 1, "00": "discard", "11": "discard"},
        "input": str(input_path),
        "input_bits": int(len(input_bits)),
        "output_bits": int(len(output_bits)),
        "padding_bits_in_final_byte": int((-len(output_bits)) % 8),
        "efficiency": float(len(output_bits) / len(input_bits)),
        "output_proportion_ones": float(output_bits.mean()) if len(output_bits) else None,
        "output_sha256": digest(output_path),
        "warning": "Educational debiasing only; input independence/stationarity is not established.",
    }
    metadata_path = output_path.with_suffix(output_path.suffix + ".json")
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
