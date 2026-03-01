"""
Dev environment setup script.
Run once after cloning the repo:

    python scripts/setup_dev.py

Works on Windows, macOS, and Linux.
"""

import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).parent.parent
VENV_DIR = ROOT / ".venv"

if sys.platform == "win32":
    PYTHON = VENV_DIR / "Scripts" / "python.exe"
    PRECOMMIT = VENV_DIR / "Scripts" / "pre-commit.exe"
else:
    PYTHON = VENV_DIR / "bin" / "python"
    PRECOMMIT = VENV_DIR / "bin" / "pre-commit"


def step(msg: str) -> None:
    print(f"\n>>> {msg}")


def run(cmd: list, **kwargs) -> None:
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        print(f"\nFailed: {' '.join(str(c) for c in cmd)}")
        sys.exit(result.returncode)


def main() -> None:
    step("Creating virtual environment...")
    if not VENV_DIR.exists():
        venv.create(str(VENV_DIR), with_pip=True)
        print("  .venv created.")
    else:
        print("  .venv already exists, skipping.")

    step("Upgrading pip...")
    run([str(PYTHON), "-m", "pip", "install", "--upgrade", "pip", "-q"])

    step("Installing dependencies from requirements-dev.txt...")
    run(
        [
            str(PYTHON),
            "-m",
            "pip",
            "install",
            "-r",
            str(ROOT / "requirements-dev.txt"),
            "-q",
        ]
    )

    step("Installing pre-commit git hooks...")
    run([str(PRECOMMIT), "install"])

    print("\nDev environment ready. Pre-commit hooks are active.")
    print("Hooks will run automatically on every git commit.")


if __name__ == "__main__":
    main()
