"""Repository integrity, link and asset tests.

Author: Trishan Biswas
Created: 24 September 2026
Repository update: 16 October 2026
"""

from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RepositoryTests(unittest.TestCase):
    def assert_hash_manifest(self, directory: Path) -> None:
        expected = {}
        for line in (directory / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
            digest, filename = line.split(maxsplit=1)
            expected[filename] = digest.lower()

        for filename, wanted in expected.items():
            path = directory / filename
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(actual, wanted, filename)

    def test_preserved_data_hashes(self) -> None:
        self.assert_hash_manifest(ROOT / "data" / "ED-1")

    def test_cad_export_hashes(self) -> None:
        self.assert_hash_manifest(ROOT / "hardware" / "ED-4" / "cad")

    def test_local_markdown_links_exist(self) -> None:
        pattern = re.compile(r"!?\[[^]]*\]\(([^)]+)\)")
        missing: list[str] = []
        for markdown in ROOT.rglob("*.md"):
            for target in pattern.findall(markdown.read_text(encoding="utf-8")):
                target = target.strip().split("#", 1)[0]
                if not target or target.startswith(("http://", "https://", "mailto:")):
                    continue
                if not (markdown.parent / target).resolve().exists():
                    missing.append(f"{markdown.relative_to(ROOT)} -> {target}")
        self.assertEqual(missing, [])

    def test_art_assets_and_source_are_local(self) -> None:
        expected_art = (
            "quantum_fields.png",
            "quantum_circles.png",
            "quantum_walk.png",
            "quantum_mosaic.png",
        )
        for filename in expected_art:
            path = ROOT / "art" / "output" / filename
            self.assertTrue(path.is_file(), filename)
            self.assertGreater(path.stat().st_size, 0, filename)

        source_text = (ROOT / "art" / "qrng_source.py").read_text(encoding="utf-8")
        self.assertIn('"data" / "ED-1" / "qrng_bits.csv"', source_text)

    def test_hardware_photographs_exist(self) -> None:
        expected_photos = (
            "hardware/ED-1/photos/ed1-breadboard-overview.jpeg",
            "hardware/ED-1/photos/ed1-analogue-stage-closeup.jpeg",
            "hardware/ED-2/photos/ed2-breadboard-overview.jpeg",
            "hardware/ED-2/photos/ed2-analogue-stage-closeup.jpeg",
            "hardware/ED-2/photos/ed2-current-breadboard-closeup.jpeg",
            "hardware/ED-2/photos/ed2-current-system-overview.jpeg",
            "hardware/ED-4/photos/ed4-printed-enclosure.jpeg",
            "hardware/ED-4/photos/ed4-perfboard-fit-check.jpeg",
        )
        for relative_path in expected_photos:
            path = ROOT / relative_path
            self.assertTrue(path.is_file(), relative_path)
            self.assertGreater(path.stat().st_size, 0, relative_path)


if __name__ == "__main__":
    unittest.main()
