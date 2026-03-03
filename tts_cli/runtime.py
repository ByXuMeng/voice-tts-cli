"""Runtime and generation-parameter tuning helpers."""

import torch


def pick_dtype(name: str, device: str):
    """根据参数选择 torch dtype，并在 CPU 场景回退到 float32。"""
    dtype_map = {
        "bfloat16": torch.bfloat16,
        "float16": torch.float16,
        "float32": torch.float32,
    }
    dtype = dtype_map[name]
    if device.startswith("cpu") and dtype in (torch.bfloat16, torch.float16):
        return torch.float32
    return dtype


def build_generate_kwargs(args) -> dict:
    """收集并过滤 generation 参数，只保留用户显式传入的值。"""
    kwargs = {
        "max_new_tokens": args.max_new_tokens,
        "temperature": args.temperature,
        "top_p": args.top_p,
        "top_k": args.top_k,
        "repetition_penalty": args.repetition_penalty,
    }
    return {k: v for k, v in kwargs.items() if v is not None}


def apply_speed_profile(args, kwargs: dict) -> dict:
    """按速度档位补默认生成参数，用户显式参数优先。"""
    out = dict(kwargs)
    default_max_tokens = {
        "fast": 600,
        "balanced": 900,
        "quality": 1400,
    }
    out.setdefault("max_new_tokens", default_max_tokens[args.speed_mode])
    if args.speed_mode == "fast":
        out.setdefault("temperature", 0.7)
        out.setdefault("top_p", 0.9)
    return out


def configure_runtime(device: str) -> None:
    """启用常见推理性能开关。"""
    if device.startswith("cuda") and torch.cuda.is_available():
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        torch.backends.cudnn.benchmark = True
        torch.set_float32_matmul_precision("high")

