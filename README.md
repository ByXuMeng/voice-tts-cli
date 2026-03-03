# voice-tts-cli

基于 Qwen3-TTS 本地模型的命令行语音生成工具，支持：
- `0.6b-base` / `1.7b-base` 语音克隆
- `1.7b-voicedesign` 风格化语音生成
- 参考音频热加载缓存（同一参考音频二次调用更快）
- 固定模型日志文件（便于排查）

## 主要功能

- 本地模型推理（`checkpoints/`）
- `ref/` 参考音频约定目录
- 速度档位：`fast` / `balanced` / `quality`
- Base 模型参考缓存：`--enable-ref-cache`
- 自动使用项目 `.venv` 解释器运行

## 快速开始

1. 进入项目目录并安装依赖（建议在 `.venv`）
2. 将模型放入 `checkpoints/`
3. 将参考音频放入 `ref/`

示例（1.7B Base）：

```powershell
.\.venv\Scripts\python .\qwen3_tts_cli.py `
  --model 1.7b-base `
  --text "你好，这是测试语音。" `
  --ref-audio 我的.wav `
  --x-vector-only-mode `
  --speed-mode fast `
  --enable-ref-cache `
  --output .\out\demo.wav
```

示例（VoiceDesign）：

```powershell
.\.venv\Scripts\python .\qwen3_tts_cli.py `
  --model 1.7b-voicedesign `
  --text "你好，这是风格化语音测试。" `
  --instruct "女声，温柔，语速中等" `
  --output .\out\design.wav
```

## 目录说明

- `qwen3_tts_cli.py`：CLI 主入口（流程编排）
- `tts_cli/`：模块化实现（参数、路径、日志、缓存、运行时优化）
- `QWEN3_TTS_CLI_USAGE.md`：详细使用说明
- `CODE_STRUCTURE.md`：代码结构说明
- `ref/`：参考音频目录
- `ref_cache/`：参考 prompt 缓存目录
- `run_logs/`：按模型固定日志
- `out/`：生成音频输出

## 注意事项

- Base 模型默认需要 `--ref-audio`。
- 不提供 `--ref-text` 时可用 `--x-vector-only-mode`（质量可能略降）。
- 首次参考音频缓存构建会稍慢，后续命中缓存可加速。

