"""Reproduce the historical *exploratory* third-party SP 800-22 run.

Author: Trishan Biswas
Created: 14 April 2026
Repository update: 16 October 2026

This is not the official NIST STS and does not implement a complete validation
campaign. It runs one sequence, two families are skipped because the installed
package implementation is incompatible with current NumPy/SciPy, and no
pass-proportion or p-value-uniformity analysis across independent sequences is
performed. Results cannot prove quantum origin or cryptographic suitability.
"""

from __future__ import annotations

import argparse
import csv
import io
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from nist80022.ApproximateEntropy import ApproximateEntropy
from nist80022.Complexity import ComplexityTest
from nist80022.CumulativeSum import CumulativeSums
from nist80022.FrequencyTest import FrequencyTest
from nist80022.Matrix import Matrix
from nist80022.RandomExcursions import RandomExcursions
from nist80022.RunTest import RunTest
from nist80022.Serial import Serial
from nist80022.Spectral import SpectralTest
from nist80022.TemplateMatching import TemplateMatching
from nist80022.Universal import Universal


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ALPHA = 0.01


def display_path(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=PROJECT_ROOT / "data" / "ED-1" / "qrng_bits.csv")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "results" / "ED-1" / "nist" / "exploratory_output.txt")
    return parser.parse_args()


def load_bits(path: Path) -> str:
    values: list[str] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for line_number, row in enumerate(csv.DictReader(handle), start=2):
            bit = row["bit"]
            if bit not in ("0", "1"):
                raise ValueError(f"Invalid bit at line {line_number}")
            values.append(bit)
    return "".join(values)


def flatten_results(name: str, result: object) -> list[tuple[str, float]]:
    if result is None:
        return []
    if isinstance(result, tuple) and len(result) == 2 and isinstance(result[0], (float, int, np.floating)):
        return [(name, float(result[0]))]

    flattened: list[tuple[str, float]] = []
    for item in result:  # type: ignore[union-attr]
        if not isinstance(item, tuple):
            continue
        if len(item) >= 2:
            flattened.append((str(item[0]), float(item[1])))
    return flattened


def main() -> None:
    args = parse_args()
    bits = load_bits(args.input.resolve())
    tests = [
        ("Frequency (Monobit)", lambda: FrequencyTest.monobit_test(bits)),
        ("Block Frequency", lambda: FrequencyTest.block_frequency(bits)),
        ("Runs", lambda: RunTest.run_test(bits)),
        ("Longest Run", None),
        ("Binary Matrix Rank", lambda: Matrix.binary_matrix_rank_text(bits)),
        ("FFT Spectral", lambda: SpectralTest.spectral_test(bits)),
        ("Non-overlapping Template", lambda: TemplateMatching.non_overlapping_test(bits, 9)),
        ("Overlapping Template", None),
        ("Linear Complexity", lambda: ComplexityTest.linear_complexity_test(bits)),
        ("Universal (Maurer)", lambda: Universal.statistical_test(bits)),
        ("Serial", lambda: Serial.serial_test(bits)),
        ("Approximate Entropy", lambda: ApproximateEntropy.approximate_entropy_test(bits, 2)),
        ("Cumulative Sums", lambda: CumulativeSums.cumulative_sums_test(bits)),
        ("Random Excursions", lambda: RandomExcursions.random_excursions_test(bits)),
        ("Random Excursions Variant", lambda: RandomExcursions.variant_test(bits)),
    ]

    lines = [
        "EXPLORATORY THIRD-PARTY SP 800-22 RUN",
        "Not official NIST validation; not evidence of quantum origin or security.",
        f"Input: {display_path(args.input.resolve())}",
        f"Bits: {len(bits):,}",
        f"Run UTC: {datetime.now(timezone.utc).isoformat()}",
        f"Exploratory alpha: {ALPHA}",
        "",
    ]
    family_summary: list[tuple[str, str]] = []

    for name, function in tests:
        lines.append(name)
        if function is None:
            status = "SKIP (known third-party package incompatibility)"
            lines.append(f"  {status}")
            family_summary.append((name, "SKIP"))
            lines.append("")
            continue
        try:
            # Some versions of the package print debug text containing Unicode
            # characters to a legacy Windows console. Capture it so that a
            # terminal encoding cannot turn a test into a false script error.
            with redirect_stdout(io.StringIO()):
                result = function()
            values = flatten_results(name, result)
            if not values:
                raise RuntimeError("package returned no p-values")
            statuses = []
            for label, p_value in values:
                status = "PASS" if p_value >= ALPHA else "FAIL"
                statuses.append(status)
                lines.append(f"  {label}: p={p_value:.6g} [{status}]")
            family_summary.append((name, "PASS" if all(item == "PASS" for item in statuses) else "FAIL"))
        except Exception as exc:  # preserve package failure as evidence
            lines.append(f"  ERROR: {type(exc).__name__}: {exc}")
            family_summary.append((name, "ERROR"))
        lines.append("")

    lines.append("FAMILY-LEVEL SUMMARY")
    for name, status in family_summary:
        lines.append(f"  {name}: {status}")
    lines.extend([
        "",
        "Interpretation: a rejection flags statistical structure under that test's",
        "assumptions. A non-rejection is not proof of randomness, unpredictability,",
        "physical mechanism, quantum origin, or cryptographic safety.",
    ])

    output_text = "\n".join(lines) + "\n"
    args.output.resolve().parent.mkdir(parents=True, exist_ok=True)
    args.output.resolve().write_text(output_text, encoding="utf-8")
    print(output_text)
    print(f"Saved {args.output.resolve()}")


if __name__ == "__main__":
    main()
