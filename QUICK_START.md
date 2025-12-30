# Speech-to-Text MCP Server - 快速参考

## 快速安装 (3 步)

```powershell
# 1. 运行安装脚本
.\setup.ps1

# 2. 设置 Hugging Face Token
$env:HUGGINGFACE_TOKEN="hf_你的token"

# 3. 测试运行
python test_local.py
```

## 工具列表

### transcribe_audio
转录音频文件

**参数:**
- `audio_file_path` - 音频文件路径 (必需)
- `language` - 语言代码,如 "zh", "en" (可选)
- `enable_diarization` - 启用说话人分离 (可选, 默认 false)

### get_supported_formats
获取支持的音频格式

## 支持的格式
mp3, wav, m4a, flac, ogg, wma, aac, opus, webm, mp4

## 常用语言代码
- zh - 中文
- en - 英文  
- ja - 日语
- ko - 韩语
- es - 西班牙语
- fr - 法语
- de - 德语

## 项目文件说明

- `server.py` - MCP Server 主程序
- `test_local.py` - 本地测试脚本
- `setup.ps1` - 自动安装脚本
- `start.ps1` - 快速启动脚本
- `README.md` - 完整文档
- `INSTALL_GUIDE.md` - 详细安装指南
- `EXAMPLES.md` - 使用示例
- `pyproject.toml` - 项目依赖配置

## 性能说明

- 首次运行会下载模型 (~1.5GB)
- CPU 模式: 音频时长的 1-2 倍
- GPU 模式: 音频时长的 0.3-0.5 倍
- 说话人分离会增加约 50% 处理时间

## 获取 Hugging Face Token

1. https://huggingface.co/settings/tokens
2. 创建新 token
3. 接受协议:
   - https://huggingface.co/pyannote/speaker-diarization-3.1
   - https://huggingface.co/pyannote/segmentation-3.0

## MCP 客户端配置位置

**Claude Desktop:**
`%APPDATA%\Claude\claude_desktop_config.json`

**Cline (VS Code):**
VS Code 设置 → Cline → MCP Settings

参考: `mcp_config_example.json`
