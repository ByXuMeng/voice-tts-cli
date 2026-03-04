# 代码结构说明

本文档描述 `E:\AITools\voice` 当前 TTS CLI 的代码组织方式，以及各文件职责。

## 1. 目录结构（核心）

```text
E:\AITools\voice
├─ qwen3_tts_cli.py
├─ README.md
├─ QWEN3_TTS_CLI_USAGE.md
├─ CODE_STRUCTURE.md
├─ checkpoints/
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
   ├─ fs_utils.py
   ├─ paths.py
   ├─ text_io.py
   ├─ runtime.py
   └─ cache.py
```

## 2. 主入口文件

### `qwen3_tts_cli.py`
- CLI 主入口，负责流程编排。
- 主要步骤：
  1. 虚拟环境引导（自动切到 `.venv`）
  2. 解析参数
  3. 解析文本输入（`--text` 或 `--text-file`）
  4. 加载模型并生成音频
  5. 保存输出与日志

## 3. 模块职责（`tts_cli/`）

### `constants.py`
- 全局常量：
  - `MODEL_ALIASES`
  - `SUPPORTED_AUDIO_EXTS`

### `args.py`
- 命令行参数定义与解析。
- 关键参数包括：
  - 文本输入：`--text` / `--text-file`（二选一）
  - 参考缓存：默认开启，可用 `--disable-ref-cache` 关闭
  - 速度档位：`--speed-mode`

### `bootstrap.py`
- 运行环境引导。
- 若当前 Python 不是项目 `.venv`，自动重启到 `.venv\Scripts\python.exe`。

### `logging_utils.py`
- 日志初始化。
- 按模型固定日志文件名并覆盖写入。

### `paths.py`
- 路径解析：
  - 模型目录
  - `ref/` 参考音频
  - 参考音频路径（绝对/相对/文件名）

### `fs_utils.py`
- 项目根目录与用户路径解析：
  - `--project-root`
  - `VOICE_TTS_ROOT` / `VOICE_TTS_HOME`
  - 相对路径统一锚定到项目根目录

### `text_io.py`
- 文本输入解析：
  - 直接文本
  - 文本文件读取（utf-8-sig / utf-8 / gb18030 自动尝试）

### `runtime.py`
- 运行时优化与生成参数策略：
  - dtype 选择
  - speed profile 默认参数
  - CUDA 性能开关（TF32、cudnn benchmark）

### `cache.py`
- Base 模型参考 prompt 缓存：
  - 冷启动构建缓存
  - 热加载命中缓存
  - 安全序列化与旧格式兼容

## 4. 运行数据目录

### `checkpoints/`
- 本地模型权重目录。

### `ref/`
- 参考音频目录（Base 模型常用）。

### `ref_cache/`
- 参考 prompt 缓存目录。

### `run_logs/`
- 固定模型日志目录。

### `out/`
- 生成音频输出目录。

## 5. 关键流程（Base 模型）

1. 解析文本输入（`--text` 或 `--text-file`）  
2. 解析参考音频路径  
3. 默认自动启用参考缓存（除非 `--disable-ref-cache`）  
4. 调用 `generate_voice_clone(...)` 生成音频  
5. 输出 wav 与日志  

## 6. 关键流程（VoiceDesign 模型）

1. 解析文本输入（`--text` 或 `--text-file`）  
2. 使用 `text + instruct (+ language)` 调用 `generate_voice_design(...)`  
3. 输出 wav 与日志  
