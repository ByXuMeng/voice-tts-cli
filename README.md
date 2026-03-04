# voice-tts-cli

本项目用于在本地运行 Qwen3-TTS，实现离线中文语音生成，支持 Base 语音克隆与 VoiceDesign 风格化合成。

文档更新时间：`2026-03-04`

## 1. 项目功能

- 本地离线 TTS 推理（无需在线 API）
- 支持 3 个模型别名：
  - `0.6b-base`
  - `1.7b-base`
  - `1.7b-voicedesign`
- Base 模型语音克隆（参考音频 + 参考文本）
- Base 模型参考音频 Prompt 热缓存（同参考音频复用更快）
- 速度档位控制（`fast` / `balanced` / `quality`）
- 统一日志系统（每模型一个固定日志文件，每次运行覆盖）
- 支持 `--text` 或 `--text-file` 输入
- 支持项目根目录迁移（`--project-root` / 环境变量）

## 2. 项目目录结构

```text
voice/
├─ qwen3_tts_cli.py                 # 入口脚本（自动切换到项目 .venv）
├─ requirements.txt                 # 环境依赖清单
├─ README.md                        # 使用文档
├─ checkpoints/                     # 本地模型目录
│  ├─ Qwen3-TTS-12Hz-0.6B-Base/
│  ├─ Qwen3-TTS-12Hz-1.7B-Base/
│  └─ Qwen3-TTS-12Hz-1.7B-VoiceDesign/
├─ ref/                             # 参考音频目录（推荐放 here）
├─ out/                             # 默认输出目录
├─ logs/                            # 日志目录（每模型一个固定文件）
├─ ref_cache/                       # 参考 Prompt 缓存目录
└─ tts_cli/                         # 核心实现
   ├─ __init__.py
   ├─ args.py                       # CLI 参数定义
   ├─ bootstrap.py                  # 虚拟环境引导
   ├─ cache.py                      # Base 模型参考 Prompt 缓存
   ├─ constants.py                  # 模型别名与音频扩展名
   ├─ fs_utils.py                   # 项目根目录/路径解析
   ├─ logging_utils.py              # 日志器初始化
   ├─ paths.py                      # 模型与参考音频路径解析
   ├─ runtime.py                    # dtype/速度档位/推理配置
   └─ text_io.py                    # 文本输入与编码回退
```

说明：`tts_cli` 模块已拆分，便于后续维护与扩展流式版本。

## 3. 运行方式

### 3.1 自动虚拟环境切换

直接运行入口脚本：

```powershell
python qwen3_tts_cli.py --help
```

脚本会优先尝试重启到项目虚拟环境 Python：
- `.venv/Scripts/python.exe`（Windows）
- `.venv/bin/python`（Linux/macOS）

### 3.2 路径环境变量（迁移复用）

| 变量名 | 默认值 | 说明 |
|---|---|---|
| `VOICE_TTS_ROOT` | 脚本所在目录 | 项目根目录 |
| `VOICE_TTS_HOME` | 空 | 与 `VOICE_TTS_ROOT` 同作用（兼容别名） |

路径解析优先级：
1. `--project-root`
2. `VOICE_TTS_ROOT` / `VOICE_TTS_HOME`
3. `qwen3_tts_cli.py` 所在目录

### 3.3 可选系统环境变量

| 变量名 | 默认值 | 说明 |
|---|---|---|
| `PATH`（SoX） | 系统默认 | 如依赖链需 SoX，请确保可找到 `sox.exe` |
| `PATH`（CUDA） | 系统默认 | GPU 推理时需 CUDA 运行库在系统可搜索路径中 |

## 4. 命令与参数

本项目当前是单命令入口（无子命令），核心参数如下。

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--model` | 必填 | `0.6b-base` / `1.7b-base` / `1.7b-voicedesign` |
| `--project-root` | 自动推断 | 项目根目录 |
| `--model-path` | 自动映射 | 自定义模型路径，覆盖默认 `checkpoints/<模型目录>` |
| `--text` | 二选一必填 | 直接输入文本（与 `--text-file` 互斥） |
| `--text-file` | 二选一必填 | 从文件读取文本（与 `--text` 互斥） |
| `--language` | `Chinese` | 语言提示，如 `Chinese` / `English` / `Auto` |
| `--output` | `out/output.wav` | 输出音频路径 |
| `--log-dir` | `logs` | 日志目录 |
| `--log-level` | `INFO` | `DEBUG/INFO/WARNING/ERROR` |
| `--instruct` | 空 | VoiceDesign 模型必填，控制音色与风格 |
| `--ref-audio` | 空 | Base 模型必填；支持绝对路径/相对路径/`ref` 文件名 |
| `--ref-text` | 空 | Base 模型推荐必填；不开 `--x-vector-only-mode` 时必填 |
| `--x-vector-only-mode` | 关闭 | 仅说话人向量克隆，不传 `--ref-text` 也可运行 |
| `--disable-ref-cache` | 关闭 | 关闭参考 Prompt 热缓存 |
| `--ref-cache-dir` | `ref_cache` | 参考 Prompt 缓存目录 |
| `--device` | `cuda:0` | 推理设备，如 `cuda:0` / `cpu` |
| `--speed-mode` | `balanced` | `fast` / `balanced` / `quality` |
| `--dtype` | `bfloat16` | `bfloat16` / `float16` / `float32` |
| `--attn-implementation` | `flash_attention_2` | 注意力实现，如 `flash_attention_2` / `eager` |
| `--max-new-tokens` | 自动按速度档位补值 | 最大生成 token |
| `--temperature` | 自动按速度档位补值 | 采样温度 |
| `--top-p` | 自动按速度档位补值 | nucleus sampling |
| `--top-k` | 不设置 | top-k 采样 |
| `--repetition-penalty` | 不设置 | 重复惩罚 |

速度档位默认行为：
- `fast`：默认 `max_new_tokens=600`，并补 `temperature=0.7`、`top_p=0.9`
- `balanced`：默认 `max_new_tokens=900`
- `quality`：默认 `max_new_tokens=1400`

## 5. 模型输入输出说明

### 5.1 Base 模型（`0.6b-base` / `1.7b-base`）

输入：
- 必需：`--text` 或 `--text-file`
- 必需：`--ref-audio`
- 条件必需：`--ref-text`（除非开启 `--x-vector-only-mode`）

输出：
- 单声道 WAV 文件（默认写入 `out/output.wav`）
- 控制台与日志输出耗时、采样率、样本点数

### 5.2 VoiceDesign 模型（`1.7b-voicedesign`）

输入：
- 必需：`--text` 或 `--text-file`
- 必需：`--instruct`

输出：
- 单声道 WAV 文件（默认写入 `out/output.wav`）
- 控制台与日志输出耗时、采样率、样本点数

## 6. 典型用法

### 6.1 1.7B Base 语音克隆

```powershell
python qwen3_tts_cli.py ^
  --model 1.7b-base ^
  --text "这是一次语音克隆测试。" ^
  --ref-audio "我的.wav" ^
  --ref-text "这是参考音频对应文本。" ^
  --output "out/clone_17b.wav"
```

### 6.2 0.6B Base 快速模式

```powershell
python qwen3_tts_cli.py ^
  --model 0.6b-base ^
  --text "请用快速模式生成这段语音。" ^
  --ref-audio "ref/文乐.wav" ^
  --ref-text "参考文本" ^
  --speed-mode fast ^
  --output "out/clone_fast.wav"
```

### 6.3 1.7B VoiceDesign

```powershell
python qwen3_tts_cli.py ^
  --model 1.7b-voicedesign ^
  --text "这是风格化语音生成示例。" ^
  --instruct "温柔、自然、中文女声" ^
  --output "out/voice_design.wav"
```

### 6.4 从文本文件输入

```powershell
python qwen3_tts_cli.py ^
  --model 1.7b-base ^
  --text-file "text/input.txt" ^
  --ref-audio "ref/我的.wav" ^
  --ref-text "参考文本"
```

## 7. 输出与日志说明

- 默认音频输出：`out/output.wav`
- 默认日志目录：`logs/`
- 固定日志文件：
  - `qwen3_tts_0.6b-base.log`
  - `qwen3_tts_1.7b-base.log`
  - `qwen3_tts_1.7b-voicedesign.log`
- 每次运行会覆盖对应模型上一轮日志
- 日志末尾会包含本次总耗时（`Total elapsed`）

## 8. 已知限制

- 当前为离线整句生成，不是 token 级实时流式 TTS。
- Base 模型若不开缓存，首次参考音频预处理耗时会明显更高。
- `--x-vector-only-mode` 可提升易用性，但音色稳定性可能下降。

## 9. 快速排错

- 报错 `ModuleNotFoundError: soundfile`：
  - 先检查是否进入项目 `.venv`，再安装 `soundfile`。
- 提示 `You are attempting to use Flash Attention 2 without specifying a torch dtype`：
  - 显式传入 `--dtype bfloat16`（或 `float16`）并确认模型加载参数生效。
- 报错找不到参考音频：
  - 把音频放到 `ref/`，并使用文件名或绝对路径传 `--ref-audio`。

## 10. 文档维护规则

以下变化发生时，需要同步更新本 README 与 `requirements.txt`：

- 参数变更（新增/删除/默认值变化）
- 路径解析逻辑变化（`project-root`、环境变量）
- 输出行为变化（日志命名、输出目录、缓存机制）
- 模型目录映射变化（`MODEL_ALIASES`）
- 依赖版本变化（尤其 `torch`、`flash-attn`、`qwen-tts`、`soundfile`）

建议维护步骤：
1. 运行 `python qwen3_tts_cli.py --help` 校对参数。
2. 至少实跑一条 Base 与一条 VoiceDesign 命令。
3. 对照日志检查耗时与输出路径是否符合文档。
4. 更新 README 的更新时间与变更点。
