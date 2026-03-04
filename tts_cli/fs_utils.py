"""Filesystem path helpers for portable project layouts."""

import os
from pathlib import Path


def resolve_user_path(path_value: str, base_dir: Path) -> Path:
    """Resolve user path; relative paths are anchored to base_dir."""
    raw = Path(path_value).expanduser()
    if raw.is_absolute():
        return raw.resolve()
    return (base_dir / raw).resolve()


def resolve_project_root(explicit_root: str | None, script_dir: Path) -> Path:
    """
    Resolve project root with priority:
    1) --project-root
    2) VOICE_TTS_ROOT / VOICE_TTS_HOME env vars
    3) directory of qwen3_tts_cli.py
    """
    if explicit_root:
        return resolve_user_path(explicit_root, Path.cwd())

    env_root = os.getenv("VOICE_TTS_ROOT") or os.getenv("VOICE_TTS_HOME")
    if env_root:
        return resolve_user_path(env_root, Path.cwd())

    return script_dir.resolve()

