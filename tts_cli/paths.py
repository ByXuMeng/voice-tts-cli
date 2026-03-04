"""Path resolution helpers."""

import logging
from pathlib import Path

from .constants import MODEL_ALIASES, SUPPORTED_AUDIO_EXTS
from .fs_utils import resolve_user_path


def resolve_model_path(model: str, model_path: str | None, project_root: Path) -> Path:
    """根据模型别名或 --model-path 解析本地模型目录。"""
    if model_path:
        p = resolve_user_path(model_path, project_root)
    else:
        p = project_root / "checkpoints" / MODEL_ALIASES[model]
    if not p.exists():
        raise FileNotFoundError(f"Model path not found: {p}")
    return p


def list_ref_audios(ref_dir: Path) -> list[Path]:
    """列出 ref 目录下可用的参考音频文件。"""
    if not ref_dir.exists():
        return []
    files = [p for p in ref_dir.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_AUDIO_EXTS]
    files.sort(key=lambda x: x.name.lower())
    return files


def resolve_ref_audio_path(ref_audio: str, project_root: Path, logger: logging.Logger) -> Path:
    """解析参考音频路径，支持绝对路径、相对路径和 ./ref 文件名。"""
    raw = Path(ref_audio).expanduser()
    if raw.is_absolute() and raw.exists():
        return raw

    candidates = [
        (Path.cwd() / raw).resolve(),
        (project_root / raw).resolve(),
        (project_root / "ref" / raw.name).resolve(),
    ]
    for c in candidates:
        if c.exists():
            return c
    logger.warning("Reference audio not found from input: %s", ref_audio)
    raise FileNotFoundError(f"Reference audio not found: {ref_audio}")
