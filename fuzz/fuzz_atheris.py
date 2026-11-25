#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Sebastien Rousseau
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Coverage-guided fuzzing of sync.py with Atheris (libFuzzer).

The Hypothesis properties in test_fuzz_sync.py run everywhere; this target
runs where Atheris ships wheels (Linux x86-64, CPython 3.12 to 3.14), in
CI's fuzz job, seeded from fuzz/corpus/:

    python fuzz/fuzz_atheris.py -runs=200000 fuzz/corpus

It feeds STANDARDS_TARGETS-shaped text to the parser and arbitrary bytes
to blob_of and the drift check, and fails on any exception or a target
with a blank label or path.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import atheris

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

with atheris.instrument_imports():
    import sync

SCRATCH = Path(tempfile.mkdtemp(prefix="standards-fuzz-"))


def test_one_input(data: bytes) -> None:
    """One fuzz case: parse targets, hash a file, compare two files."""
    fdp = atheris.FuzzedDataProvider(data)
    for label, path in sync._env_targets(fdp.ConsumeUnicodeNoSurrogates(256)):
        if not label or not str(path).strip():
            raise AssertionError(f"blank target from STANDARDS_TARGETS: {label!r} {path!r}")
    src, dst = SCRATCH / "src", SCRATCH / "dst"
    src.write_bytes(fdp.ConsumeBytes(fdp.ConsumeIntInRange(0, 512)))
    dst.write_bytes(fdp.ConsumeBytes(512))
    if len(sync.blob_of(src)) != 40:
        raise AssertionError("blob_of did not return a 40-character id")
    drifted = sync.check_target_file(src, dst, "F", "T", quiet=True)
    if drifted != (src.read_bytes() != dst.read_bytes()):
        raise AssertionError("check_target_file disagrees with a byte comparison")


def main() -> None:
    """Hand the target to libFuzzer with the command-line options."""
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
