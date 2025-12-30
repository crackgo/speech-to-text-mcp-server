# Speech-to-Text MCP Server

一个支持语音转文本和说话人分离的 Model Context Protocol (MCP) 服务器。

## 功能特性

- ✅ 支持上传最长 60 分钟的音频文件
- ✅ 自动语音识别 (使用 OpenAI Whisper)
- ✅ 说话人分离功能 (使用 pyannote.audio)
- ✅ 支持多种音频格式 (mp3, wav, m4a, flac 等)
- ✅ 输出带时间戳的转录文本

## 系统要求

- Python 3.10 或更高版本
- Windows/Linux/macOS
- 至少 8GB RAM (推荐 16GB)
- 建议使用 GPU 以加速处理 (可选)

## 安装步骤

### 1. 创建虚拟环境

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. 安装依赖

```powershell
pip install -e .
```

### 3. 安装 FFmpeg (音频处理必需)

**Windows:**
- 下载 FFmpeg: https://ffmpeg.org/download.html
- 解压并添加到系统 PATH

**或使用 Chocolatey:**
```powershell
choco install ffmpeg
```

### 4. 获取 Hugging Face Token

pyannote.audio 需要 Hugging Face token:

1. 访问 https://huggingface.co/settings/tokens
2. 创建一个新的 token
3. 接受模型使用条款:
   - https://huggingface.co/pyannote/speaker-diarization-3.1
   - https://huggingface.co/pyannote/segmentation-3.0

## 配置 MCP 客户端

在你的 MCP 客户端配置文件中添加此服务器:

```json
{
  "mcpServers": {
    "speech-to-text": {
      "command": "python",
      "args": [
        "e:\\demoProject\\speech_to_text\\server.py"
      ],
      "env": {
        "HUGGINGFACE_TOKEN": "your_token_here"
      }
    }
  }
}
```

## 使用方法

服务器提供以下工具:

### 1. transcribe_audio

转录音频文件为文本。

**参数:**
- `audio_file_path` (必需): 音频文件的完整路径
- `language` (可选): 语言代码,如 "zh" (中文), "en" (英文), 默认自动检测
- `enable_diarization` (可选): 是否启用说话人分离,默认 false

**示例调用:**

```json
{
  "audio_file_path": "C:\\Users\\username\\Desktop\\meeting.mp3",
  "language": "zh",
  "enable_diarization": true
}
```

### 2. get_supported_formats

获取支持的音频格式列表。

## 输出示例

### 不启用说话人分离:

```
[00:00:00.000 --> 00:00:05.000] 大家好,欢迎参加今天的会议。
[00:00:05.000 --> 00:00:12.000] 今天我们主要讨论项目进展。
```

### 启用说话人分离:

```
[说话人 SPEAKER_00] [00:00:00.000 --> 00:00:05.000]
大家好,欢迎参加今天的会议。

[说话人 SPEAKER_01] [00:00:05.000 --> 00:00:12.000]
今天我们主要讨论项目进展。
```

## 技术细节

- **语音识别引擎**: OpenAI Whisper (medium 模型)
- **说话人分离**: pyannote.audio 3.1
- **音频处理**: pydub + FFmpeg
- **MCP 版本**: 1.0

## 性能建议

- 对于长音频 (>30分钟),建议使用 GPU
- 首次运行会下载模型文件 (~1.5GB)
- 处理时间大约为音频时长的 0.5-2 倍 (取决于硬件)

## 故障排除

### 问题: FFmpeg 未找到
**解决**: 确保 FFmpeg 已安装并在 PATH 中

### 问题: CUDA out of memory
**解决**: 使用 CPU 模式或减少 batch size

### 问题: pyannote.audio 认证失败
**解决**: 检查 HUGGINGFACE_TOKEN 是否正确设置并接受了模型条款

## 许可证

MIT License
