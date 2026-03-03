# 代码结构说明

本文档描述 `E:\AITools\voice` 当前 TTS CLI 的代码组织方式，以及各文件职责。

## 1. 目录结构（核心）

```text
E:\AITools\voice
├─ qwen3_tts_cli.py
├─ QWEN3_TTS_CLI_USAGE.md
├─ CODE_STRUCTURE.md
├─ checkpoints/
│  ├─ Qwen3-TTS-12Hz-0.6B-Base/
│  ├─ Qwen3-TTS-12Hz-1.7B-Base/
│  └─ Qwen3-TTS-12Hz-1.7B-VoiceDesign/
├─ ref/
├─ ref_cache/
├─ run_logs/
├─ out/
└─ tts_cli/
   ├─ __init__.py
   ├─ constants.py
   ├─ args.py
   ├─ bootstrap.py
   ├─ logging_utils.py
   ├─ paths.py
   ├─ runtime.py
   └─ cache.py
```

## 2. 主入口文件

### `qwen3_tts_cli.py`
- CLI 主入口，负责“流程编排”。
- 主要步骤：
  1. 虚拟环境引导（自动切到 `.venv`）。
  2. 解析参数。
  3. 初始化日志。
  4. 解析模型路径与运行参数。
  5. 加载模型并执行生成。
  6. 保存音频、输出耗时与日志路径。
- 不承担复杂业务细节，细节全部下沉到 `tts_cli/`。

## 3. 模块职责（`tts_cli/`）

### `tts_cli/constants.py`
- 全局常量：
  - `MODEL_ALIASES`：模型别名到目录名映射。
  - `SUPPORTED_AUDIO_EXTS`：参考音频支持格式。

### `tts_cli/args.py`
- 命令行参数定义与解析。
- 包含模型选择、日志参数、速度档位、参考音频缓存参数等。

### `tts_cli/bootstrap.py`
- 运行环境引导。
- 若当前 Python 不是项目 `.venv`，自动重启到 `.venv\Scripts\python.exe`。

### `tts_cli/logging_utils.py`
- 日志系统初始化。
- 采用“按模型固定文件名 + 每次覆写”的策略：
  - `qwen3_tts_0.6b-base.log`
  - `qwen3_tts_1.7b-base.log`
  - `qwen3_tts_1.7b-voicedesign.log`

### `tts_cli/paths.py`
- 路径相关逻辑：
  - 解析模型目录（默认 `checkpoints/...`）。
  - 列出 `ref/` 可用参考音频。
  - 解析参考音频路径（绝对/相对/仅文件名）。

### `tts_cli/runtime.py`
- 运行时性能与生成参数策略：
  - dtype 选择（CPU 自动回退 `float32`）。
  - `speed-mode` 档位参数注入（`fast/balanced/quality`）。
  - CUDA 推理优化开关（TF32、cudnn benchmark 等）。

### `tts_cli/cache.py`
- Base 模型参考音频热加载缓存。
- 关键能力：
  - 生成稳定缓存键（模型 + 参考音频 + 参数）。
  - 首次冷加载创建缓存，后续命中热加载。
  - 缓存对象安全序列化（兼容 PyTorch 2.6+ `weights_only` 行为）。

## 4. 运行时数据目录

### `checkpoints/`
- 本地模型权重目录（3 个模型）。

### `ref/`
- 参考音频目录（Base 模型常用）。

### `ref_cache/`
- 参考 prompt 缓存目录。
- 命中时可减少参考音频预处理时间。

### `run_logs/`
- 每模型一份固定日志，重复运行会覆写同模型日志文件。

### `out/`
- 生成的音频输出目录。

## 5. 关键执行流程（Base 模型）

1. 读取参数与模型路径。  
2. 加载模型。  
3. 解析 `ref-audio`。  
4. 若开启 `--enable-ref-cache`：
   - 先查 `ref_cache` 是否命中。
   - 未命中则从参考音频构建 prompt 并写缓存。
5. 调用 `generate_voice_clone(...)` 生成音频。  
6. 写入 `out/*.wav`，日志记录总耗时。  

## 6. 关键执行流程（VoiceDesign 模型）

1. 读取参数与模型路径。  
2. 加载模型。  
3. 使用 `text + instruct (+ language)` 调用 `generate_voice_design(...)`。  
4. 写入 `out/*.wav`，日志记录总耗时。  

## 7. 维护建议

1. 新增参数优先放在 `tts_cli/args.py`，并在 `qwen3_tts_cli.py` 显式编排使用。  
2. 运行时优化策略统一在 `tts_cli/runtime.py` 管理，避免分散在主流程。  
3. 缓存键逻辑若变更，优先修改 `tts_cli/cache.py` 的 `build_ref_cache_path`。  
4. 说明文档同步维护：
   - `QWEN3_TTS_CLI_USAGE.md`
   - `CODE_STRUCTURE.md`

