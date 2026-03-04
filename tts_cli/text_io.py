"""Text loading helpers for CLI input."""

from pathlib import Path


def resolve_input_text(text: str | None, text_file: str | None, base_dir: Path) -> tuple[str, str]:
    """Resolve text from direct input or file; returns (text, source)."""
    if text is not None:
        stripped = text.strip()
        if not stripped:
            raise ValueError("--text is empty.")
        return stripped, "inline"

    if not text_file:
        raise ValueError("Either --text or --text-file is required.")

    raw = Path(text_file).expanduser()
    path = raw.resolve() if raw.is_absolute() else (base_dir / raw).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Text file not found: {path}")

    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            content = path.read_text(encoding=encoding)
            stripped = content.strip()
            if not stripped:
                raise ValueError(f"Text file is empty: {path}")
            return stripped, f"file:{path} ({encoding})"
        except UnicodeDecodeError:
            continue

    raise UnicodeDecodeError("text_file", b"", 0, 1, f"Unable to decode text file: {path}")
