"""Command line argument definitions."""

import argparse

from .constants import MODEL_ALIASES


def parse_args() -> argparse.Namespace:
    """解析命令行参数，定义必填与可选项。"""
    parser = argparse.ArgumentParser(
        description="Run local Qwen3-TTS checkpoints to generate audio."
    )
    parser.add_argument("--model", choices=MODEL_ALIASES.keys(), required=True)
    parser.add_argument("--model-path", default=None, help="Override local model path.")
    parser.add_argument("--text", required=True, help="Input text to synthesize.")
    parser.add_argument("--language", default="Chinese", help="Language name, e.g. English/Chinese/Auto.")
    parser.add_argument("--output", default="output.wav", help="Output wav path.")
    parser.add_argument("--log-dir", default="logs", help="Directory for timestamped run logs.")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log verbosity.",
    )

    parser.add_argument("--instruct", default=None, help="Required for voice design model.")
    parser.add_argument(
        "--ref-audio",
        default=None,
        help="Required for Base models. Supports absolute path, relative path, or filename under ./ref.",
    )
    parser.add_argument("--ref-text", default=None, help="Transcript for reference audio.")
    parser.add_argument(
        "--x-vector-only-mode",
        action="store_true",
        help="Allow voice clone without ref_text (quality may drop).",
    )
    parser.add_argument(
        "--enable-ref-cache",
        action="store_true",
        help="Enable hot-loading cache for Base model reference prompt.",
    )
    parser.add_argument(
        "--ref-cache-dir",
        default="ref_cache",
        help="Directory to store reference prompt cache files.",
    )

    parser.add_argument("--device", default="cuda:0", help="Device map, e.g. cuda:0 or cpu.")
    parser.add_argument(
        "--speed-mode",
        choices=["fast", "balanced", "quality"],
        default="balanced",
        help="Speed/quality preset. fast is quickest, quality allows longer generation.",
    )
    parser.add_argument(
        "--dtype",
        choices=["bfloat16", "float16", "float32"],
        default="bfloat16",
        help="Model dtype.",
    )
    parser.add_argument(
        "--attn-implementation",
        default="flash_attention_2",
        help="Attention backend, e.g. flash_attention_2 or eager.",
    )

    parser.add_argument("--max-new-tokens", type=int, default=None)
    parser.add_argument("--temperature", type=float, default=None)
    parser.add_argument("--top-p", type=float, default=None)
    parser.add_argument("--top-k", type=int, default=None)
    parser.add_argument("--repetition-penalty", type=float, default=None)
    return parser.parse_args()

