"""Audit a captured ADC/LSB dataset and generate source diagnostics.

Author: Trishan Biswas
Created: 14 April 2026
Repository update: 16 October 2026
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = PROJECT_ROOT / "data" / "ED-1" / "qrng_bits.csv"
DEFAULT_FIGURE = PROJECT_ROOT / "figures" / "ED-1" / "source_diagnostics.png"
DEFAULT_REPORT = PROJECT_ROOT / "results" / "ED-1" / "april_2026_dataset_audit.json"


def display_path(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--figure", type=Path, default=DEFAULT_FIGURE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--max-lag", type=int, default=100)
    parser.add_argument("--block-size", type=int, default=1000)
    return parser.parse_args()


def load_capture(path: Path) -> tuple[np.ndarray, np.ndarray]:
    raw_values: list[int] = []
    bits: list[int] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not {"raw", "bit"}.issubset(reader.fieldnames):
            raise ValueError(f"{path} must contain raw and bit columns")
        for line_number, row in enumerate(reader, start=2):
            try:
                raw = int(row["raw"])
                bit = int(row["bit"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid value at CSV line {line_number}") from exc
            if bit not in (0, 1):
                raise ValueError(f"Bit outside 0/1 at CSV line {line_number}")
            if not 0 <= raw <= 1023:
                raise ValueError(f"ADC value outside 0-1023 at CSV line {line_number}")
            if bit != (raw & 1):
                raise ValueError(f"Bit does not match raw ADC LSB at CSV line {line_number}")
            raw_values.append(raw)
            bits.append(bit)
    if not bits:
        raise ValueError(f"{path} contains no samples")
    return np.asarray(raw_values, dtype=np.float64), np.asarray(bits, dtype=np.uint8)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def shannon_entropy(bits: np.ndarray) -> float:
    p1 = float(np.mean(bits))
    probabilities = (p1, 1.0 - p1)
    return -sum(p * math.log2(p) for p in probabilities if p > 0)


def longest_run(bits: np.ndarray) -> int:
    if bits.size == 0:
        return 0
    boundaries = np.flatnonzero(np.diff(bits)) + 1
    lengths = np.diff(np.concatenate(([0], boundaries, [bits.size])))
    return int(lengths.max())


def autocorrelation_fft(values: np.ndarray, max_lag: int) -> np.ndarray:
    centred = values.astype(np.float64) - float(np.mean(values))
    if not np.any(centred):
        return np.full(max_lag + 1, np.nan)
    fft_length = 1 << (2 * len(centred) - 1).bit_length()
    spectrum = np.fft.rfft(centred, n=fft_length)
    correlation = np.fft.irfft(spectrum * np.conjugate(spectrum), n=fft_length)
    correlation = correlation[: max_lag + 1]
    overlap = np.arange(len(centred), len(centred) - max_lag - 1, -1)
    correlation = correlation / overlap
    return correlation / correlation[0]


def block_entropies(bits: np.ndarray, block_size: int) -> np.ndarray:
    count = len(bits) // block_size
    if count == 0:
        return np.asarray([], dtype=float)
    blocks = bits[: count * block_size].reshape(count, block_size)
    p1 = blocks.mean(axis=1)
    p0 = 1.0 - p1
    with np.errstate(divide="ignore", invalid="ignore"):
        term1 = np.where(p1 > 0, -p1 * np.log2(p1), 0.0)
        term0 = np.where(p0 > 0, -p0 * np.log2(p0), 0.0)
    return term0 + term1


def power_spectrum(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    centred = values.astype(np.float64) - float(np.mean(values))
    windowed = centred * np.hanning(len(centred))
    spectrum = np.fft.rfft(windowed)
    power = np.abs(spectrum) ** 2
    frequencies = np.fft.rfftfreq(len(centred), d=1.0)
    power[0] = 0.0
    total = float(power.sum())
    if total:
        power /= total
    return frequencies, power


def audit(path: Path, max_lag: int, block_size: int) -> tuple[dict, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    raw, bits = load_capture(path)
    n = len(bits)
    if max_lag < 1 or max_lag >= n:
        raise ValueError("max_lag must be between 1 and the sample count minus one")
    if block_size < 1:
        raise ValueError("block_size must be positive")
    ones = int(bits.sum())
    p1 = ones / n
    raw_acf = autocorrelation_fft(raw, max_lag)
    bit_acf = autocorrelation_fft(bits, max_lag)
    blocks = block_entropies(bits, block_size)
    frequencies, power = power_spectrum(raw)
    dominant_index = int(np.argmax(power))
    dominant_frequency = float(frequencies[dominant_index])

    transitions = np.zeros((2, 2), dtype=np.int64)
    np.add.at(transitions, (bits[:-1], bits[1:]), 1)

    report = {
        "input": display_path(path),
        "sha256": file_sha256(path),
        "samples": n,
        "ones": ones,
        "zeros": n - ones,
        "proportion_ones": p1,
        "binary_shannon_entropy": shannon_entropy(bits),
        "most_common_value_estimate": -math.log2(max(p1, 1.0 - p1)),
        "longest_identical_bit_run": longest_run(bits),
        "raw_adc": {
            "minimum": int(raw.min()),
            "maximum": int(raw.max()),
            "mean": float(raw.mean()),
            "standard_deviation": float(raw.std()),
            "lag_1_correlation": float(raw_acf[1]),
            "dominant_cycles_per_sample": dominant_frequency,
            "dominant_period_samples": 1.0 / dominant_frequency if dominant_frequency else None,
        },
        "lsb_lag_1_correlation": float(bit_acf[1]),
        "transition_counts": transitions.tolist(),
        "block_size": block_size,
        "block_entropy_mean": float(blocks.mean()) if len(blocks) else None,
        "notes": [
            "Descriptive audit only; not a NIST SP 800-90B entropy assessment.",
            "The most-common-value estimate ignores dependence and non-stationarity.",
        ],
    }
    return report, raw, bits, raw_acf, bit_acf


def make_figure(path: Path, raw: np.ndarray, bits: np.ndarray, raw_acf: np.ndarray, bit_acf: np.ndarray, block_size: int, title: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    entropies = block_entropies(bits, block_size)
    trace_count = min(3000, len(raw))
    lags = np.arange(len(raw_acf))
    frequencies, power = power_spectrum(raw)

    fig, axes = plt.subplots(2, 3, figsize=(16, 8))

    axes[0, 0].plot(np.arange(trace_count), raw[:trace_count], color="#235789", linewidth=0.7)
    axes[0, 0].set(title=f"Raw ADC trace (first {trace_count:,} samples)", xlabel="Sample", ylabel="ADC code")

    bins = np.arange(int(raw.min()), int(raw.max()) + 2)
    axes[0, 1].hist(raw, bins=bins, color="#235789", alpha=0.9)
    axes[0, 1].set(title="Raw ADC distribution", xlabel="ADC code", ylabel="Count")

    axes[0, 2].semilogy(frequencies[1:], np.maximum(power[1:], np.finfo(float).tiny), color="#d95f02", linewidth=0.8)
    axes[0, 2].set(title="Raw ADC power spectrum", xlabel="Cycles per sample", ylabel="Normalised power")

    axes[1, 0].plot(lags[1:], raw_acf[1:], color="#d95f02")
    axes[1, 0].axhline(0, color="black", linewidth=0.7)
    axes[1, 0].set(title="Raw ADC autocorrelation", xlabel="Lag (samples)", ylabel="Correlation")

    axes[1, 1].plot(lags[1:], bit_acf[1:], color="#1b9e77")
    axes[1, 1].axhline(0, color="black", linewidth=0.7)
    axes[1, 1].set(title="LSB autocorrelation", xlabel="Lag (samples)", ylabel="Correlation", ylim=(-0.01, 0.01))

    axes[1, 2].plot(np.arange(len(entropies)) * block_size, entropies, color="#6a3d9a", linewidth=0.8)
    axes[1, 2].axhline(1.0, color="black", linestyle="--", linewidth=0.8)
    axes[1, 2].set(title=f"Entropy in non-overlapping {block_size}-bit blocks", xlabel="Starting sample", ylabel="bit/symbol", ylim=(0.97, 1.002))

    for axis in axes.flat:
        axis.grid(alpha=0.2)
    fig.suptitle(title, fontweight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    input_path = args.input.resolve()
    report, raw, bits, raw_acf, bit_acf = audit(input_path, args.max_lag, args.block_size)
    make_figure(
        args.figure.resolve(),
        raw,
        bits,
        raw_acf,
        bit_acf,
        args.block_size,
        f"{input_path.stem}: source diagnostics",
    )
    args.report.resolve().parent.mkdir(parents=True, exist_ok=True)
    args.report.resolve().write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Figure: {args.figure.resolve()}")
    print(f"Report: {args.report.resolve()}")


if __name__ == "__main__":
    main()
