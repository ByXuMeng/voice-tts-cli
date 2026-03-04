"""Environment bootstrap helpers."""

import subprocess
import sys
from pathlib import Path


def _find_venv_python(script_dir: Path) -> Path | None:
    """Find local venv python on Windows/Linux/macOS."""
    candidates = [
        script_dir / ".venv" / "Scripts" / "python.exe",  # Windows
        script_dir / ".venv" / "bin" / "python",          # POSIX
    ]
    for c in candidates:
        if c.exists():
            return c.resolve()
    return None


def ensure_local_venv_python(script_file: str) -> None:
    """确保脚本在项目 .venv 的 Python 下运行，不一致时自动重启。"""
    script_path = Path(script_file).resolve()
    script_dir = script_path.parent
    venv_python = _find_venv_python(script_dir)
    current_python = Path(sys.executable).resolve()

    if venv_python is None:
        return
    if current_python == venv_python:
        return

    print(f"[bootstrap] Re-launching with virtualenv python: {venv_python}")
    result = subprocess.run([str(venv_python), str(script_path), *sys.argv[1:]])
    raise SystemExit(result.returncode)
