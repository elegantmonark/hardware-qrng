"""Tests for the QRNG analysis and extraction functions.

Author: Trishan Biswas
Created: 24 September 2026
Repository update: 16 October 2026
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np


PYTHON_DIR = Path(__file__).resolve().parents[1] / "software"
sys.path.insert(0, str(PYTHON_DIR))

import analyser  # noqa: E402
import extract  # noqa: E402


class AnalysisTests(unittest.TestCase):
    def test_shannon_entropy_extremes(self) -> None:
        self.assertAlmostEqual(analyser.shannon_entropy(np.array([0, 1], dtype=np.uint8)), 1.0)
        self.assertAlmostEqual(analyser.shannon_entropy(np.array([0, 0], dtype=np.uint8)), 0.0)

    def test_longest_run(self) -> None:
        bits = np.array([0, 0, 1, 1, 1, 0], dtype=np.uint8)
        self.assertEqual(analyser.longest_run(bits), 3)

    def test_von_neumann_mapping(self) -> None:
        # 01 -> 0, 10 -> 1, while 00 and 11 are discarded.
        bits = np.array([0, 1, 1, 0, 0, 0, 1, 1], dtype=np.uint8)
        np.testing.assert_array_equal(extract.von_neumann(bits), np.array([0, 1], dtype=np.uint8))

    def test_autocorrelation_for_alternating_sequence(self) -> None:
        values = np.tile(np.array([0, 1], dtype=np.uint8), 100)
        result = analyser.autocorrelation_fft(values, 2)
        self.assertAlmostEqual(float(result[1]), -1.0, places=6)
        self.assertAlmostEqual(float(result[2]), 1.0, places=6)


if __name__ == "__main__":
    unittest.main()
