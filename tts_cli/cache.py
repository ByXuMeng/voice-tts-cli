"""Reference-prompt caching for Base voice-clone models."""

import hashlib
import logging
from pathlib import Path

import torch
from qwen_tts import Qwen3TTSModel
from qwen_tts.inference.qwen3_tts_model import VoiceClonePromptItem


def build_ref_cache_path(
    cache_dir: Path,
    model_alias: str,
    ref_audio_path: Path,
    ref_text: str | None,
    x_vector_only_mode: bool,
) -> Path:
    """根据参考音频和关键参数生成稳定缓存文件名。"""
    stat = ref_audio_path.stat()
    key_src = "|".join(
        [
            model_alias,
            str(ref_audio_path.resolve()),
            str(stat.st_size),
            str(int(stat.st_mtime)),
            ref_text or "",
            str(bool(x_vector_only_mode)),
        ]
    )
    key = hashlib.sha1(key_src.encode("utf-8")).hexdigest()[:16]
    return cache_dir / f"{model_alias}_{key}.pt"


def prompt_items_to_cpu(items: list[VoiceClonePromptItem]) -> list[VoiceClonePromptItem]:
    """将 prompt item 内的 tensor 转到 CPU，便于跨设备缓存与加载。"""
    out: list[VoiceClonePromptItem] = []
    for it in items:
        ref_code = it.ref_code.detach().cpu() if it.ref_code is not None else None
        ref_spk_embedding = it.ref_spk_embedding.detach().cpu()
        out.append(
            VoiceClonePromptItem(
                ref_code=ref_code,
                ref_spk_embedding=ref_spk_embedding,
                x_vector_only_mode=it.x_vector_only_mode,
                icl_mode=it.icl_mode,
                ref_text=it.ref_text,
            )
        )
    return out


def serialize_prompt_items(items: list[VoiceClonePromptItem]) -> list[dict]:
    """将 prompt item 序列化为纯 dict，避免 torch.load 安全限制。"""
    return [
        {
            "ref_code": it.ref_code,
            "ref_spk_embedding": it.ref_spk_embedding,
            "x_vector_only_mode": bool(it.x_vector_only_mode),
            "icl_mode": bool(it.icl_mode),
            "ref_text": it.ref_text,
        }
        for it in items
    ]


def deserialize_prompt_items(payload: object) -> list[VoiceClonePromptItem]:
    """从缓存 payload 反序列化为 VoiceClonePromptItem 列表。"""
    if isinstance(payload, list) and payload and isinstance(payload[0], VoiceClonePromptItem):
        return payload
    if isinstance(payload, list) and (len(payload) == 0 or isinstance(payload[0], dict)):
        out: list[VoiceClonePromptItem] = []
        for d in payload:
            out.append(
                VoiceClonePromptItem(
                    ref_code=d.get("ref_code", None),
                    ref_spk_embedding=d["ref_spk_embedding"],
                    x_vector_only_mode=bool(d.get("x_vector_only_mode", False)),
                    icl_mode=bool(d.get("icl_mode", not bool(d.get("x_vector_only_mode", False)))),
                    ref_text=d.get("ref_text", None),
                )
            )
        return out
    raise ValueError("Unsupported prompt cache format.")


def get_or_build_voice_clone_prompt(
    model: Qwen3TTSModel,
    model_alias: str,
    ref_audio_path: Path,
    ref_text: str | None,
    x_vector_only_mode: bool,
    cache_dir: Path,
    enable_cache: bool,
    logger: logging.Logger,
) -> list[VoiceClonePromptItem]:
    """获取或构建 Base 模型的 reference prompt（支持磁盘缓存热加载）。"""
    if not enable_cache:
        logger.info("Reference cache disabled, building prompt from audio...")
        return model.create_voice_clone_prompt(
            ref_audio=str(ref_audio_path),
            ref_text=ref_text,
            x_vector_only_mode=x_vector_only_mode,
        )

    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = build_ref_cache_path(
        cache_dir=cache_dir,
        model_alias=model_alias,
        ref_audio_path=ref_audio_path,
        ref_text=ref_text,
        x_vector_only_mode=x_vector_only_mode,
    )
    if cache_path.exists():
        logger.info("Reference cache hit: %s", cache_path)
        try:
            loaded = torch.load(cache_path, map_location="cpu")
            return deserialize_prompt_items(loaded)
        except Exception:
            # 兼容旧缓存: 本地可信文件允许 fallback 读取后重写为安全格式。
            loaded = torch.load(cache_path, map_location="cpu", weights_only=False)
            items = deserialize_prompt_items(loaded)
            torch.save(serialize_prompt_items(items), cache_path)
            return items

    logger.info("Reference cache miss, building prompt...")
    items = model.create_voice_clone_prompt(
        ref_audio=str(ref_audio_path),
        ref_text=ref_text,
        x_vector_only_mode=x_vector_only_mode,
    )
    items_cpu = prompt_items_to_cpu(items)
    torch.save(serialize_prompt_items(items_cpu), cache_path)
    logger.info("Reference cache saved: %s", cache_path)
    return items_cpu

