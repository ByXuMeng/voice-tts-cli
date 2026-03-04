"""Command line argument definitions."""

import argparse

from .constants import MODEL_ALIASES


class RichHelpFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter):
    """Show defaults and preserve newlines in help text."""


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        prog="qwen3_tts_cli.py",
        formatter_class=RichHelpFormatter,
        description=(
            "Local Qwen3-TTS CLI for voice cloning and voice design.\n"
            "Model modes:\n"
            "  - Base models (0.6b-base / 1.7b-base): require --ref-audio\n"
            "  - VoiceDesign model (1.7b-voicedesign): require --instruct"
        ),
        epilog=(
            "Quick examples:\n"
            "  Base clone:\n"
            "    python qwen3_tts_cli.py --model 1.7b-base --text \"你好\" --ref-audio ref.wav --ref-text \"你好\"\n"
            "  VoiceDesign:\n"
            "    python qwen3_tts_cli.py --model 1.7b-voicedesign --text \"你好\" --instruct \"温柔、自然、中文女声\"\n"
            "  From text file:\n"
            "    python qwen3_tts_cli.py --model 0.6b-base --text-file text/input.txt --ref-audio ref.wav --ref-text \"参考文本\""
        ),
    )

    required = parser.add_argument_group("Required Core Arguments")
    required.add_argument(
        "--model",
        choices=MODEL_ALIASES.keys(),
        required=True,
        help="Model alias.",
    )
    text_group = required.add_mutually_exclusive_group(required=True)
    text_group.add_argument("--text", metavar="TEXT", help="Input text to synthesize.")
    text_group.add_argument("--text-file", metavar="FILE", help="Read input text from a local file.")

    path_group = parser.add_argument_group("Path and Output")
    path_group.add_argument(
        "--project-root",
        metavar="DIR",
        default=None,
        help="Project root. Relative paths resolve from here.",
    )
    path_group.add_argument(
        "--model-path",
        metavar="DIR",
        default=None,
        help="Override local model directory.",
    )
    path_group.add_argument("--output", metavar="WAV", default="out/output.wav", help="Output wav path.")
    path_group.add_argument("--log-dir", metavar="DIR", default="logs", help="Directory for log files.")
    path_group.add_argument(
        "--ref-cache-dir",
        metavar="DIR",
        default="ref_cache",
        help="Directory for Base model reference-prompt cache.",
    )

    mode_group = parser.add_argument_group("Mode-Specific Arguments")
    mode_group.add_argument(
        "--instruct",
        metavar="TEXT",
        default=None,
        help="Required when --model=1.7b-voicedesign.",
    )
    mode_group.add_argument(
        "--ref-audio",
        metavar="PATH_OR_NAME",
        default=None,
        help="Required for Base models. Supports absolute path, relative path, or filename under ./ref.",
    )
    mode_group.add_argument(
        "--ref-text",
        metavar="TEXT",
        default=None,
        help="Reference transcript for Base models (required unless --x-vector-only-mode).",
    )
    mode_group.add_argument(
        "--x-vector-only-mode",
        action="store_true",
        help="Allow Base clone without --ref-text (may reduce quality).",
    )
    mode_group.add_argument(
        "--disable-ref-cache",
        action="store_true",
        help="Disable Base reference-prompt cache (cold build every run).",
    )
    mode_group.add_argument(
        "--language",
        metavar="LANG",
        default="Chinese",
        help="Language hint, e.g. Chinese / English / Auto.",
    )

    runtime_group = parser.add_argument_group("Runtime and Performance")
    runtime_group.add_argument("--device", metavar="DEVICE", default="cuda:0", help="Device, e.g. cuda:0 or cpu.")
    runtime_group.add_argument(
        "--speed-mode",
        choices=["fast", "balanced", "quality"],
        default="balanced",
        help=(
            "Speed/quality preset.\n"
            "  fast: lower latency\n"
            "  balanced: default\n"
            "  quality: allow longer generation"
        ),
    )
    runtime_group.add_argument(
        "--dtype",
        choices=["bfloat16", "float16", "float32"],
        default="bfloat16",
        help="Model dtype.",
    )
    runtime_group.add_argument(
        "--attn-implementation",
        metavar="IMPL",
        default="flash_attention_2",
        help="Attention backend, e.g. flash_attention_2 or eager.",
    )
    runtime_group.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log verbosity level.",
    )

    tune_group = parser.add_argument_group("Advanced Generation Tuning (Optional)")
    tune_group.add_argument("--max-new-tokens", metavar="N", type=int, default=None, help="Max generation tokens.")
    tune_group.add_argument("--temperature", metavar="T", type=float, default=None, help="Sampling temperature.")
    tune_group.add_argument("--top-p", metavar="P", type=float, default=None, help="Nucleus sampling p.")
    tune_group.add_argument("--top-k", metavar="K", type=int, default=None, help="Top-k sampling.")
    tune_group.add_argument(
        "--repetition-penalty",
        metavar="R",
        type=float,
        default=None,
        help="Penalty for repeated tokens.",
    )
    return parser.parse_args()
