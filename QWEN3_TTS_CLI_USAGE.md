# qwen3_tts_cli.py 使用说明

脚本路径: `E:\AITools\voice\qwen3_tts_cli.py`

## 1. 运行方式
推荐命令:

```powershell
python E:\AITools\voice\qwen3_tts_cli.py --model <model> --text <text> [args...]
```

说明:
- 脚本内置了虚拟环境引导逻辑。
- 如果当前不是项目 `.venv`，脚本会自动重启到 `E:\AITools\voice\.venv\Scripts\python.exe` 执行。

可用模型:
- `0.6b-base`
- `1.7b-base`
- `1.7b-voicedesign`

## 2. ref 目录约定
- 参考音频统一放在: `E:\AITools\voice\ref\`
- Base 模型可以直接写文件名:
  - `--ref-audio demo.wav`
- 脚本会优先从 `./ref` 查找该文件。
- 如果 Base 模型未传 `--ref-audio`，脚本会列出 `ref` 目录中的候选音频并提醒你选择。

## 3. 必传参数
所有模型都必传:
- `--model`
- `--text`

按模型额外必传:
- `1.7b-voicedesign`:
  - `--instruct`
- `0.6b-base` / `1.7b-base`:
  - `--ref-audio`
  - `--ref-text` (除非使用 `--x-vector-only-mode`)

## 4. 可选参数
通用:
- `--model-path` 自定义模型目录
- `--language` 语言, 默认 `Chinese`
- `--output` 输出 wav 路径, 默认 `output.wav`
- `--device` 默认 `cuda:0`
- `--speed-mode` `fast|balanced|quality`, 默认 `balanced`
- `--dtype` `bfloat16|float16|float32`, 默认 `bfloat16`
- `--attn-implementation` 默认 `flash_attention_2`

日志:
- `--log-dir` 日志目录, 默认 `logs`
- `--log-level` `DEBUG|INFO|WARNING|ERROR`, 默认 `INFO`
- 日志按模型固定命名并覆盖写入:
  - `qwen3_tts_0.6b-base.log`
  - `qwen3_tts_1.7b-base.log`
  - `qwen3_tts_1.7b-voicedesign.log`

生成参数:
- `--max-new-tokens`
- `--temperature`
- `--top-p`
- `--top-k`
- `--repetition-penalty`

速度档位说明:
- `fast`: 速度优先, 默认 `max_new_tokens=600`
- `balanced`: 平衡模式, 默认 `max_new_tokens=900`
- `quality`: 质量优先, 默认 `max_new_tokens=1400`
- 如果你手动传了 `--max-new-tokens`，会覆盖上面的默认值

Base 模型专用:
- `--x-vector-only-mode`
- `--enable-ref-cache` 启用参考音频热加载缓存
- `--ref-cache-dir` 参考缓存目录, 默认 `ref_cache`

## 5. 示例
VoiceDesign:

```powershell
python E:\AITools\voice\qwen3_tts_cli.py `
  --model 1.7b-voicedesign `
  --text "你好，这是语音设计测试。" `
  --instruct "温柔女声，语速中等" `
  --output E:\AITools\voice\out\voicedesign.wav
```

0.6B Base (从 ref 目录读参考音频):

```powershell
python E:\AITools\voice\qwen3_tts_cli.py `
  --model 0.6b-base `
  --text "这是 0.6B 克隆测试。" `
  --ref-audio demo.wav `
  --ref-text "这是参考音频对应文本。" `
  --output E:\AITools\voice\out\clone_06b.wav
```

1.7B Base:

```powershell
python E:\AITools\voice\qwen3_tts_cli.py `
  --model 1.7b-base `
  --text "这是 1.7B 克隆测试。" `
  --ref-audio demo.wav `
  --ref-text "这是参考音频对应文本。" `
  --speed-mode fast `
  --temperature 0.7 `
  --top-p 0.9 `
  --output E:\AITools\voice\out\clone_17b.wav
```

Base 模型加速推荐（参考音频热缓存）:

```powershell
python E:\AITools\voice\qwen3_tts_cli.py `
  --model 1.7b-base `
  --text "这是缓存加速测试。" `
  --ref-audio 我的.wav `
  --x-vector-only-mode `
  --speed-mode fast `
  --enable-ref-cache `
  --ref-cache-dir E:\AITools\voice\ref_cache `
  --output E:\AITools\voice\out\clone_cached.wav
```

说明:
- 第一次会创建缓存（稍慢）。
- 后续同一参考音频 + 同一关键参数会直接命中缓存，减少前处理时间。

## 6. 输出
每次运行会生成:
- 音频文件 (`wav`)
- 对应模型的固定日志文件 (每次运行覆盖上一次), 默认在:
  - `logs\qwen3_tts_0.6b-base.log`
  - `logs\qwen3_tts_1.7b-base.log`
  - `logs\qwen3_tts_1.7b-voicedesign.log`
