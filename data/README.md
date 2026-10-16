# Data

Datasets are separated by demonstrator and must retain their provenance.

- `ED-1/qrng_bits.csv` is the preserved April 2026 physical source capture containing one million samples.
- `ED-1/prng_bits.csv` is the corresponding software control stream used in the published comparison.
- `ED-1/SHA256SUMS` records the integrity hashes for those files.
- `ED-2/runs/` is the default local destination for new timestamped captures and is ignored by Git until a run is deliberately selected for publication.

Do not overwrite ED-1 files with ED-2 output. A published ED-2 capture should include its metadata sidecar, cryptographic hash, circuit identifier, firmware identifier, sample count, and relevant environmental notes.
