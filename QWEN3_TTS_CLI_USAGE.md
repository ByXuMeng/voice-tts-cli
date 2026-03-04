# qwen3_tts_cli.py 使用说明

脚本路径: `E:\AITools\voice\qwen3_tts_cli.py`

## 1. 运行方式

推荐命令：

```powershell
python E:\AITools\voice\qwen3_tts_cli.py --model <model> (--text <text> | --text-file <file>) [args...]
```

说明：
- 脚本内置虚拟环境引导：如果当前不是项目 `.venv`，会自动重启到 `E:\AITools\voice\.venv\Scripts\python.exe`。
- 文本输入支持二选一：
  - `--text`
  - `--text-file`

可用模型：
- `0.6b-base`
- `1.7b-base`
- `1.7b-voicedesign`

## 2. ref 目录约定

- 参考音频建议放在：`E:\AITools\voice\ref\`
- Base 模型可直接写文件名：
  - `--ref-audio sample.wav`
- 脚本会优先从 `./ref` 查找文件。
- 若 Base 模型未传 `--ref-audio`，脚本会列出 `ref` 目录可用音频并提示选择。

## 3. 必传参数

所有模型都必传：
- `--model`
- `--text` 或 `--text-file`（二选一）

按模型额外必传：
- `1.7b-voicedesign`
  - `--instruct`
- `0.6b-base` / `1.7b-base`
  - `--ref-audio`
  - `--ref-text`（除非使用 `--x-vector-only-mode`）

## 4. 可选参数

通用：
- `--project-root` 项目根目录（相对路径参数都基于此目录解析）
- `--model-path` 自定义模型目录
- `--language` 语言，默认 `Chinese`
- `--output` 输出 wav 路径，默认 `out/output.wav`
- `--device` 默认 `cuda:0`
- `--speed-mode` `fast|balanced|quality`，默认 `balanced`
- `--dtype` `bfloat16|float16|float32`，默认 `bfloat16`
- `--attn-implementation` 默认 `flash_attention_2`

环境变量：
- `VOICE_TTS_ROOT` 或 `VOICE_TTS_HOME` 可作为默认项目根目录（优先级低于 `--project-root`）

日志：
- `--log-dir` 日志目录，默认 `logs`
- `--log-level` `DEBUG|INFO|WARNING|ERROR`，默认 `INFO`
- 日志按模型固定命名并覆盖写入：
  - `qwen3_tts_0.6b-base.log`
  - `qwen3_tts_1.7b-base.log`
  - `qwen3_tts_1.7b-voicedesign.log`

生成参数：
- `--max-new-tokens`
- `--temperature`
- `--top-p`
- `--top-k`
- `--repetition-penalty`

速度档位说明：
- `fast`: 速度优先，默认 `max_new_tokens=600`
- `balanced`: 平衡模式，默认 `max_new_tokens=900`
- `quality`: 质量优先，默认 `max_new_tokens=1400`
- 手动传 `--max-new-tokens` 会覆盖默认值

Base 模型专用：
- `--x-vector-only-mode`
- 默认启用参考音频热加载缓存
- `--disable-ref-cache` 关闭缓存
- `--ref-cache-dir` 缓存目录，默认 `ref_cache`

## 5. 示例

VoiceDesign（文本直传）：

```powershell
python E:\AITools\voice\qwen3_tts_cli.py `
  --model 1.7b-voicedesign `
  --text "你好，这是语音设计测试。" `
  --instruct "温柔女声，语速中等" `
  --output E:\AITools\voice\out\voicedesign.wav
```

0.6B Base（文本文件输入）：

```powershell
python E:\AITools\voice\qwen3_tts_cli.py `
  --model 0.6b-base `
  --text-file E:\AITools\voice\text\input.txt `
  --ref-audio sample.wav `
  --ref-text "这是参考音频对应文本。" `
  --output E:\AITools\voice\out\clone_06b.wav
```

1.7B Base（缓存加速）：

```powershell
python E:\AITools\voice\qwen3_tts_cli.py `
  --model 1.7b-base `
  --text "这是缓存加速测试。" `
  --ref-audio sample.wav `
  --x-vector-only-mode `
  --speed-mode fast `
  --ref-cache-dir E:\AITools\voice\ref_cache `
  --output E:\AITools\voice\out\clone_cached.wav
```

## 6. 输出

每次运行会生成：
- 音频文件（`wav`）
- 对应模型固定日志（每次覆盖上一次）
