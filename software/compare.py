"""Compare the captured LSB stream with the saved PRNG control fairly.

Author: Trishan Biswas
Created: 14 April 2026
Repository update: 16 October 2026
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, default=PROJECT_ROOT / "data" / "ED-1" / "qrng_bits.csv")
    parser.add_argument("--control", type=Path, default=PROJECT_ROOT / "data" / "ED-1" / "prng_bits.csv")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "figures" / "ED-1" / "comparison.png")
    parser.add_argument("--block-size", type=int, default=500)
    return parser.parse_args()


def load(path: Path) -> tuple[np.ndarray, np.ndarray]:
    raw: list[int] = []
    bits: list[int] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not {"raw", "bit"}.issubset(reader.fieldnames):
            raise ValueError(f"{path} must contain raw and bit columns")
        for line_number, row in enumerate(reader, start=2):
            value = int(row["raw"])
            bit = int(row["bit"])
            if bit not in (0, 1):
                raise ValueError(f"Invalid bit at CSV line {line_number}")
            raw.append(value)
            bits.append(bit)
    if not bits:
        raise ValueError(f"{path} contains no samples")
    return np.asarray(raw), np.asarray(bits, dtype=np.uint8)


def block_entropy(bits: np.ndarray, size: int) -> np.ndarray:
    count = len(bits) // size
    blocks = bits[: count * size].reshape(count, size)
    p1 = blocks.mean(axis=1)
    p0 = 1.0 - p1
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(p1 > 0, -p1 * np.log2(p1), 0) + np.where(p0 > 0, -p0 * np.log2(p0), 0)


def main() -> None:
    args = parse_args()
    if args.block_size < 1:
        raise SystemExit("--block-size must be positive")
    captured_raw, captured_bits = load(args.capture.resolve())
    _, control_bits = load(args.control.resolve())
    common_n = min(len(captured_bits), len(control_bits))
    if common_n < args.block_size:
        raise SystemExit("Not enough common samples for the chosen block size")

    captured = captured_bits[:common_n]
    control = control_bits[:common_n]
    captured_h = block_entropy(captured, args.block_size)
    control_h = block_entropy(control, args.block_size)
    positions = np.arange(len(captured_h)) * args.block_size

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))

    axes[0].plot(positions, captured_h, marker=".", label="captured LSB", color="#235789")
    axes[0].plot(positions, control_h, marker=".", label="Mersenne Twister", color="#f18f01")
    axes[0].axhline(1.0, color="black", linestyle="--", linewidth=0.8)
    axes[0].set(title=f"Block entropy ({args.block_size} bits)", xlabel="Sample", ylabel="bit/symbol", ylim=(0.975, 1.002))
    axes[0].legend()

    percentages = np.array([
        100 * np.mean(captured == 0),
        100 * np.mean(captured == 1),
        100 * np.mean(control == 0),
        100 * np.mean(control == 1),
    ])
    bars = axes[1].bar(["capture\n0", "capture\n1", "control\n0", "control\n1"], percentages, color=["#235789", "#235789", "#f18f01", "#f18f01"])
    axes[1].axhline(50, color="black", linestyle="--", linewidth=0.8)
    axes[1].set(title=f"Bit balance (first {common_n:,} bits each)", ylabel="Percent", ylim=(45, 55))
    for bar, value in zip(bars, percentages):
        axes[1].text(bar.get_x() + bar.get_width() / 2, value + 0.15, f"{value:.2f}%", ha="center", fontsize=9)

    bins = np.arange(int(captured_raw.min()), int(captured_raw.max()) + 2)
    axes[2].hist(captured_raw, bins=bins, color="#235789")
    axes[2].set(title="Raw ADC distribution (full capture)", xlabel="ADC code", ylabel="Count")

    for axis in axes:
        axis.grid(alpha=0.2)
    fig.suptitle("Captured LSB stream and deterministic PRNG control", fontweight="bold")
    fig.text(0.5, 0.01, "Similarity in these plots does not establish physical origin or security.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    args.output.resolve().parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output.resolve(), dpi=200)
    plt.close(fig)
    print(f"Compared {common_n:,} bits from each source")
    print(f"Saved {args.output.resolve()}")


if __name__ == "__main__":
    main()
