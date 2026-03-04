import time
from pathlib import Path

from tts_cli.args import parse_args
from tts_cli.bootstrap import ensure_local_venv_python


def main() -> None:
    """Main flow: bootstrap env, load model, generate audio, save outputs and logs."""
    run_start = time.time()
    args = parse_args()
    ensure_local_venv_python(__file__)

    # Delay heavy imports until after venv bootstrap and arg parsing.
    import soundfile as sf
    from qwen_tts import Qwen3TTSModel

    from tts_cli.cache import get_or_build_voice_clone_prompt
    from tts_cli.fs_utils import resolve_project_root, resolve_user_path
    from tts_cli.logging_utils import setup_logger
    from tts_cli.paths import list_ref_audios, resolve_model_path, resolve_ref_audio_path
    from tts_cli.runtime import apply_speed_profile, build_generate_kwargs, configure_runtime, pick_dtype
    from tts_cli.text_io import resolve_input_text

    script_dir = Path(__file__).resolve().parent
    project_root = resolve_project_root(args.project_root, script_dir)
    logger, log_path = setup_logger(args.log_dir, args.log_level, args.model, project_root)
    ref_dir = project_root / "ref"
    ref_dir.mkdir(parents=True, exist_ok=True)
    input_text, text_source = resolve_input_text(args.text, args.text_file, project_root)

    logger.info("Run started")
    logger.info("Project root: %s", project_root)
    logger.info("Model alias: %s", args.model)
    logger.info("Output: %s", resolve_user_path(args.output, project_root))
    logger.info("Text source: %s", text_source)

    model_path = resolve_model_path(args.model, args.model_path, project_root)
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
    # Force dtype consistency for FlashAttention checks in some backends.
    try:
        model.model.config.torch_dtype = dtype
    except Exception:
        pass
    try:
        param_dtype = next(model.model.parameters()).dtype
        if param_dtype != dtype:
            model.model.to(dtype=dtype)
    except Exception:
        pass
    logger.info("Model loaded in %.2fs", time.time() - t0)

    t1 = time.time()
    logger.info("Generating audio...")
    if args.model.endswith("voicedesign"):
        if not args.instruct:
            raise ValueError("--instruct is required for 1.7b-voicedesign")
        wavs, sr = model.generate_voice_design(
            text=input_text,
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

        ref_audio_path = resolve_ref_audio_path(args.ref_audio, project_root, logger)
        logger.info("Reference audio: %s", ref_audio_path)
        prompt_start = time.time()
        prompt_items = get_or_build_voice_clone_prompt(
            model=model,
            model_alias=args.model,
            ref_audio_path=ref_audio_path,
            ref_text=args.ref_text,
            x_vector_only_mode=args.x_vector_only_mode,
            cache_dir=resolve_user_path(args.ref_cache_dir, project_root),
            enable_cache=not args.disable_ref_cache,
            logger=logger,
        )
        logger.info("Prompt ready in %.2fs", time.time() - prompt_start)
        wavs, sr = model.generate_voice_clone(
            text=input_text,
            language=args.language,
            voice_clone_prompt=prompt_items,
            **gen_kwargs,
        )
    logger.info("Generation finished in %.2fs", time.time() - t1)

    output = resolve_user_path(args.output, project_root)
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
