import time
from pathlib import Path

import soundfile as sf
from qwen_tts import Qwen3TTSModel

from tts_cli.args import parse_args
from tts_cli.bootstrap import ensure_local_venv_python
from tts_cli.cache import get_or_build_voice_clone_prompt
from tts_cli.logging_utils import setup_logger
from tts_cli.paths import list_ref_audios, resolve_model_path, resolve_ref_audio_path
from tts_cli.runtime import apply_speed_profile, build_generate_kwargs, configure_runtime, pick_dtype


def main() -> None:
    """主流程：环境引导、加载模型、执行推理、保存音频与日志。"""
    run_start = time.time()
    ensure_local_venv_python(__file__)
    args = parse_args()
    logger, log_path = setup_logger(args.log_dir, args.log_level, args.model)
    script_dir = Path(__file__).resolve().parent
    ref_dir = script_dir / "ref"
    ref_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Run started")
    logger.info("Model alias: %s", args.model)
    logger.info("Output: %s", Path(args.output).expanduser().resolve())

    model_path = resolve_model_path(args.model, args.model_path, script_dir)
    dtype = pick_dtype(args.dtype, args.device)
    gen_kwargs = apply_speed_profile(args, build_generate_kwargs(args))
    configure_runtime(args.device)
    logger.info("Resolved model path: %s", model_path)
    logger.info(
        "Device: %s | Dtype: %s | Attn: %s | Speed: %s",
        args.device,
        dtype,
        args.attn_implementation,
        args.speed_mode,
    )
    logger.info("Generation kwargs: %s", gen_kwargs)

    t0 = time.time()
    logger.info("Loading model...")
    model = Qwen3TTSModel.from_pretrained(
        str(model_path),
        device_map=args.device,
        dtype=dtype,
        attn_implementation=args.attn_implementation,
    )
    logger.info("Model loaded in %.2fs", time.time() - t0)

    t1 = time.time()
    logger.info("Generating audio...")
    if args.model.endswith("voicedesign"):
        if not args.instruct:
            raise ValueError("--instruct is required for 1.7b-voicedesign")
        wavs, sr = model.generate_voice_design(
            text=args.text,
            language=args.language,
            instruct=args.instruct,
            **gen_kwargs,
        )
    else:
        if not args.ref_audio:
            ref_files = list_ref_audios(ref_dir)
            if ref_files:
                logger.error("--ref-audio is required for Base voice clone models.")
                logger.error("Available reference audios in %s:", ref_dir)
                for idx, file_path in enumerate(ref_files, start=1):
                    logger.error("  %d. %s", idx, file_path.name)
                raise ValueError("Please choose one file from ./ref and pass it via --ref-audio <filename>")
            raise ValueError("--ref-audio is required for Base voice clone models (no audio found in ./ref)")
        if not args.ref_text and not args.x_vector_only_mode:
            raise ValueError("--ref-text is required unless --x-vector-only-mode is set")

        ref_audio_path = resolve_ref_audio_path(args.ref_audio, script_dir, logger)
        logger.info("Reference audio: %s", ref_audio_path)
        prompt_start = time.time()
        prompt_items = get_or_build_voice_clone_prompt(
            model=model,
            model_alias=args.model,
            ref_audio_path=ref_audio_path,
            ref_text=args.ref_text,
            x_vector_only_mode=args.x_vector_only_mode,
            cache_dir=Path(args.ref_cache_dir).expanduser().resolve(),
            enable_cache=args.enable_ref_cache,
            logger=logger,
        )
        logger.info("Prompt ready in %.2fs", time.time() - prompt_start)
        wavs, sr = model.generate_voice_clone(
            text=args.text,
            language=args.language,
            voice_clone_prompt=prompt_items,
            **gen_kwargs,
        )
    logger.info("Generation finished in %.2fs", time.time() - t1)

    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(output), wavs[0], sr)
    logger.info("Saved wav: %s", output)
    logger.info("Sample rate: %s | Samples: %s", sr, len(wavs[0]))
    total_elapsed = time.time() - run_start
    logger.info("Total elapsed: %.2fs", total_elapsed)
    logger.info("Log file: %s", log_path)

    print(f"Saved: {output}")
    print(f"Sample rate: {sr}")
    print(f"Samples: {len(wavs[0])}")
    print(f"Total elapsed: {total_elapsed:.2f}s")
    print(f"Log: {log_path}")


if __name__ == "__main__":
    main()

