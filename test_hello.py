"""Acceptance tests for hello.py.

The tests prove that the program prints exactly Hello World and that the
interpreter running it is at or above the version pinned in
.python-version. Run them from the repository root with the pinned
interpreter and ``-m unittest -v``, as README.md describes.
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path

# Directory holding this file, hello.py and .python-version. Resolving paths
# against it keeps the tests independent of the working directory.
ROOT = Path(__file__).resolve().parent


class HelloWorldTest(unittest.TestCase):
    """Acceptance tests for the Hello World program and its interpreter."""

    def test_prints_hello_world(self) -> None:
        """Prove the program prints exactly Hello World and nothing else.

        hello.py runs in a real subprocess under this same interpreter. It
        must exit with status 0, write "Hello World" and the platform line
        terminator to stdout, and write nothing to stderr. A hung run
        raises subprocess.TimeoutExpired, which unittest reports as an
        error.
        """
        result = subprocess.run(
            [sys.executable, str(ROOT / "hello.py")],
            capture_output=True,
            timeout=30,
            check=False,
        )
        # The literal is written here rather than imported from hello.py,
        # so a typo in the program cannot also pass the test. os.linesep
        # matches the terminator print() emits: text-mode stdout writes
        # "\r\n" for "\n" on Windows.
        expected = ("Hello World" + os.linesep).encode("ascii")
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr!r}")
        self.assertEqual(result.stdout, expected)
        self.assertEqual(result.stderr, b"")

    def test_interpreter_meets_pinned_version(self) -> None:
        """Prove the interpreter is at or above the pin in .python-version.

        The pin is a floor, not an exact match, so a newer interpreter also
        passes. The exact release is confirmed separately by the version
        check that README.md documents. The minimum is read only from
        .python-version, so moving to a newer release needs no edit here.
        A pin not of the form X.Y or X.Y.Z raises ValueError, which
        unittest reports as an error rather than a failure.
        """
        pin_path = ROOT / ".python-version"
        pin = pin_path.read_text(encoding="utf-8").strip()
        parts = pin.split(".")
        # int() alone would accept a sign, underscores, non-ASCII digits or
        # any number of components, so a malformed pin could lower the floor
        # instead of being rejected.
        if not (
            2 <= len(parts) <= 3
            and all(part.isascii() and part.isdecimal() for part in parts)
        ):
            raise ValueError(
                f"{pin_path} must hold a version of the form X.Y or X.Y.Z "
                f"using ASCII digits only; found {pin!r}"
            )
        required = tuple(int(part) for part in parts)
        running = tuple(sys.version_info[:3])
        running_str = ".".join(str(part) for part in running)
        self.assertGreaterEqual(
            running,
            required,
            f"Python {pin} or newer is required; running {running_str}",
        )


if __name__ == "__main__":
    unittest.main()
