"""Collect raw ADC samples and LSBs from the serial sampler.

Author: Trishan Biswas
Created: 14 April 2026
ED-2 update: 16 October 2026

This program records measurements; it does not assume that the measured noise
is quantum or that the extracted bits are secure.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import serial
from serial.tools import list_ports


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def available_ports() -> list[str]:
    return [item.device for item in list_ports.comports()]


def resolve_port(requested: str | None) -> str:
    if requested:
        return requested
    ports = available_ports()
    if len(ports) == 1:
        return ports[0]
    if not ports:
        raise SystemExit("No serial ports found. Connect the sampler or pass --port.")
    joined = "\n  ".join(ports)
    raise SystemExit(f"More than one serial port found. Choose one with --port:\n  {joined}")


def default_output() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return PROJECT_ROOT / "data" / "ED-2" / "runs" / f"capture_{stamp}.csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", help="Serial port, for example COM3 or /dev/cu.usbserial-...")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--samples", type=int, default=1_000_000)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output CSV (default: timestamped file in data/ED-2/runs)",
    )
    parser.add_argument("--reset-delay", type=float, default=2.0)
    parser.add_argument("--progress-every", type=int, default=10_000)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--demonstrator", default="ED-2")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--list-ports", action="store_true")
    return parser.parse_args()


def open_serial(port: str, baud: int, reset_delay: float) -> serial.Serial:
    try:
        connection = serial.Serial(port, baud, timeout=1)
    except serial.SerialException as exc:
        raise SystemExit(f"Could not open {port}: {exc}") from exc
    time.sleep(reset_delay)
    connection.reset_input_buffer()
    return connection


def collect(args: argparse.Namespace) -> Path:
    if args.samples < 1:
        raise SystemExit("--samples must be positive")
    if args.baud < 1:
        raise SystemExit("--baud must be positive")
    if args.reset_delay < 0:
        raise SystemExit("--reset-delay cannot be negative")
    if args.progress_every < 1:
        raise SystemExit("--progress-every must be positive")
    if args.max_retries < 0:
        raise SystemExit("--max-retries cannot be negative")

    port = resolve_port(args.port)
    output = (args.output or default_output()).resolve()
    if output.exists() and not args.overwrite:
        raise SystemExit(f"Refusing to overwrite {output}. Use --overwrite or another --output.")
    output.parent.mkdir(parents=True, exist_ok=True)

    started_utc = datetime.now(timezone.utc)
    started_clock = time.perf_counter()
    collected = 0
    invalid_lines = 0
    reconnects = 0
    interrupted = False

    print(f"Collecting {args.samples:,} samples from {port} at {args.baud} baud")
    print(f"Writing {output}")

    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["sample_index", "elapsed_ms", "raw", "bit"])

        while collected < args.samples:
            connection = open_serial(port, args.baud, args.reset_delay)
            segment_start = time.perf_counter()
            try:
                while collected < args.samples:
                    try:
                        line = connection.readline().decode("utf-8", errors="ignore").strip()
                    except serial.SerialException as exc:
                        print(f"Serial connection lost: {exc}", file=sys.stderr)
                        break
                    if not line:
                        continue
                    try:
                        raw_text, bit_text = line.split(",")
                        raw = int(raw_text)
                        bit = int(bit_text)
                    except (ValueError, TypeError):
                        invalid_lines += 1
                        continue
                    if not 0 <= raw <= 1023 or bit not in (0, 1) or bit != (raw & 1):
                        invalid_lines += 1
                        continue

                    elapsed_ms = 1000.0 * (time.perf_counter() - started_clock)
                    writer.writerow([collected, f"{elapsed_ms:.3f}", raw, bit])
                    collected += 1

                    if collected % args.progress_every == 0:
                        elapsed = time.perf_counter() - started_clock
                        rate = collected / elapsed
                        print(f"  {collected:>10,}/{args.samples:,}  {rate:8.1f} samples/s")
            except KeyboardInterrupt:
                interrupted = True
                print("\nCollection interrupted; preserving the partial capture.")
            finally:
                connection.close()

            if interrupted or collected >= args.samples:
                break
            reconnects += 1
            if reconnects > args.max_retries:
                print("Maximum reconnect count reached; preserving the partial capture.", file=sys.stderr)
                break
            print(f"Reconnecting ({reconnects}/{args.max_retries}); previous segment lasted "
                  f"{time.perf_counter() - segment_start:.1f} s")
            time.sleep(2)

    finished_utc = datetime.now(timezone.utc)
    metadata = {
        "schema_version": 1,
        "started_utc": started_utc.isoformat(),
        "finished_utc": finished_utc.isoformat(),
        "port": port,
        "baud": args.baud,
        "requested_samples": args.samples,
        "recorded_samples": collected,
        "invalid_serial_lines": invalid_lines,
        "reconnects": reconnects,
        "interrupted": interrupted,
        "demonstrator": args.demonstrator,
        "platform": platform.platform(),
        "python": platform.python_version(),
        "csv_sha256": sha256(output),
        "notes": "Add component IDs, measured supplies, ADC reference and temperature manually.",
    }
    metadata_path = output.with_suffix(".json")
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    print(f"Saved {collected:,} samples")
    print(f"SHA-256: {metadata['csv_sha256']}")
    print(f"Metadata: {metadata_path}")
    return output


def main() -> None:
    args = parse_args()
    if args.list_ports:
        ports = available_ports()
        print("\n".join(ports) if ports else "No serial ports found")
        return
    collect(args)


if __name__ == "__main__":
    main()
