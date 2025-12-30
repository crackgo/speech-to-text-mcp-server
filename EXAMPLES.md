# 使用示例

## 快速开始示例

### 示例 1: 基本转录(无说话人分离)

假设你有一个音频文件 `meeting.mp3`:

```json
{
  "tool": "transcribe_audio",
  "arguments": {
    "audio_file_path": "C:\\Users\\YourName\\Desktop\\meeting.mp3",
    "language": "zh"
  }
}
```

**输出示例:**
```
=== 转录结果 ===
文件: meeting.mp3
时长: 15.3 分钟
语言: zh
说话人分离: 否
==================================================

[00:00:00.000 --> 00:00:05.120] 大家好,欢迎参加今天的会议。
[00:00:05.120 --> 00:00:10.500] 今天我们主要讨论三个议题。
[00:00:10.500 --> 00:00:15.800] 第一个议题是关于项目进度。
```

---

### 示例 2: 启用说话人分离

```json
{
  "tool": "transcribe_audio",
  "arguments": {
    "audio_file_path": "C:\\Users\\YourName\\Desktop\\meeting.mp3",
    "language": "zh",
    "enable_diarization": true
  }
}
```

**输出示例:**
```
=== 转录结果 ===
文件: meeting.mp3
时长: 15.3 分钟
语言: zh
说话人分离: 是
==================================================

[说话人 SPEAKER_00] [00:00:00.000 --> 00:00:05.120]
大家好,欢迎参加今天的会议。

[说话人 SPEAKER_01] [00:00:05.120 --> 00:00:10.500]
谢谢主持人,我先介绍一下项目背景。

[说话人 SPEAKER_00] [00:00:10.500 --> 00:00:15.800]
好的,请继续。
```

---

### 示例 3: 英文音频自动检测

```json
{
  "tool": "transcribe_audio",
  "arguments": {
    "audio_file_path": "C:\\Users\\YourName\\Desktop\\podcast.mp3"
  }
}
```

系统会自动检测语言并转录。

---

### 示例 4: 查看支持的格式

```json
{
  "tool": "get_supported_formats",
  "arguments": {}
}
```

**输出:**
```
支持的音频格式:
- mp3
- wav
- m4a
- flac
- ogg
- wma
- aac
- opus
- webm
- mp4
```

---

## 常见使用场景

### 场景 1: 会议记录
- 上传会议录音
- 启用说话人分离
- 获得带时间戳和说话人标识的完整记录

### 场景 2: 访谈转录
- 上传访谈音频
- 指定语言(如果已知)
- 快速获取文字稿

### 场景 3: 播客/讲座笔记
- 上传音频文件
- 自动识别语言
- 获得时间戳对齐的文本

---

## MCP 客户端配置示例

### Claude Desktop 配置

编辑 `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "speech-to-text": {
      "command": "python",
      "args": [
        "e:\\demoProject\\speech_to_text\\server.py"
      ],
      "env": {
        "HUGGINGFACE_TOKEN": "hf_xxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

### Cline (VS Code) 配置

在 VS Code 的 Cline 设置中添加:

```json
{
  "mcpServers": {
    "speech-to-text": {
      "command": "python",
      "args": [
        "e:\\demoProject\\speech_to_text\\server.py"
      ],
      "env": {
        "HUGGINGFACE_TOKEN": "hf_xxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

---

## 语言代码参考

常用语言代码:
- `zh`: 中文
- `en`: 英文
- `ja`: 日语
- `ko`: 韩语
- `es`: 西班牙语
- `fr`: 法语
- `de`: 德语
- `ru`: 俄语

完整列表请参考: https://github.com/openai/whisper#available-models-and-languages

---

## 性能预估

基于不同硬件的处理时间参考:

| 音频时长 | CPU (无GPU) | GPU (NVIDIA RTX 3060) |
|---------|-------------|----------------------|
| 5 分钟  | ~5-10 分钟  | ~2-3 分钟           |
| 30 分钟 | ~30-60 分钟 | ~10-15 分钟         |
| 60 分钟 | ~60-120 分钟| ~20-30 分钟         |

*说话人分离会增加约 50% 的处理时间*
