# MCP Server 客户端配置指南

本指南帮助你将 Speech-to-Text MCP Server 添加到各种 AI 客户端。

---

## 📋 前置要求

1. ✅ 已安装 Python 环境（conda 环境 `mcpserver`）
2. ✅ 已配置 HUGGINGFACE_TOKEN 环境变量
3. ✅ 确保 MCP Server 可以正常运行

---

## 🔧 方法一：Claude Desktop（推荐）

### 1. 找到配置文件位置

**Windows 系统：**
```
%APPDATA%\Claude\claude_desktop_config.json
```
完整路径通常是：
```
C:\Users\你的用户名\AppData\Roaming\Claude\claude_desktop_config.json
```

### 2. 编辑配置文件

打开 `claude_desktop_config.json`，添加以下配置：

```json
{
  "mcpServers": {
    "speech-to-text": {
      "command": "conda",
      "args": [
        "run",
        "-n",
        "mcpserver",
        "--no-capture-output",
        "python",
        "E:\\demoProject\\speech_to_text\\server.py"
      ],
      "env": {
        "HUGGINGFACE_TOKEN": "你的HuggingFace_Token"
      }
    }
  }
}
```

**注意：**
- 如果文件中已有其他 MCP 服务器，在 `mcpServers` 下添加 `speech-to-text` 配置
- 路径使用双反斜杠 `\\` 或单斜杠 `/`
- 替换 `你的HuggingFace_Token` 为实际的 token

### 3. 重启 Claude Desktop

完全退出 Claude Desktop（右键托盘图标 -> 退出），然后重新启动。

### 4. 验证连接

在 Claude 中询问：
```
你能帮我转录语音文件吗？
```

如果 Claude 提到可以使用 `transcribe_audio` 工具，说明配置成功！

---

## 🔧 方法二：Cherry Studio

Cherry Studio 使用不同的配置方式。

### 1. 找到配置文件

Cherry Studio 的 MCP 配置文件通常在：
```
C:\Users\你的用户名\.cherry-studio\mcp_servers.json
```

或通过设置界面配置（推荐）。

### 2. 通过设置界面添加

1. 打开 Cherry Studio
2. 进入 **设置 -> MCP Servers**
3. 点击 **添加服务器**
4. 填写以下信息：

```
名称: Speech-to-Text
命令: conda
参数: run -n mcpserver --no-capture-output python E:\demoProject\speech_to_text\server.py
环境变量: HUGGINGFACE_TOKEN=你的token
```

### 3. 或手动编辑配置文件

```json
{
  "servers": [
    {
      "name": "speech-to-text",
      "command": "conda",
      "args": [
        "run",
        "-n",
        "mcpserver",
        "--no-capture-output",
        "python",
        "E:\\demoProject\\speech_to_text\\server.py"
      ],
      "env": {
        "HUGGINGFACE_TOKEN": "你的HuggingFace_Token"
      },
      "enabled": true
    }
  ]
}
```

---

## 🔧 方法三：其他 MCP 兼容客户端

### 通用配置格式

大多数 MCP 客户端都支持类似的配置格式：

```json
{
  "speech-to-text": {
    "command": "conda",
    "args": [
      "run",
      "-n",
      "mcpserver",
      "--no-capture-output",
      "python",
      "E:\\demoProject\\speech_to_text\\server.py"
    ],
    "env": {
      "HUGGINGFACE_TOKEN": "你的token"
    }
  }
}
```

---

## 🔧 方法四：直接使用 Python 启动（开发测试）

如果客户端不支持 conda，可以使用完整的 Python 路径：

### 1. 获取 Python 路径

在 PowerShell 中运行：
```powershell
conda activate mcpserver
python -c "import sys; print(sys.executable)"
```

假设输出是：
```
C:\Anaconda\envs\mcpserver\python.exe
```

### 2. 使用该路径配置

```json
{
  "speech-to-text": {
    "command": "C:\\Anaconda\\envs\\mcpserver\\python.exe",
    "args": [
      "E:\\demoProject\\speech_to_text\\server.py"
    ],
    "env": {
      "HUGGINGFACE_TOKEN": "你的token"
    }
  }
}
```

---

## 📝 获取 HuggingFace Token

如果还没有 HuggingFace Token：

1. 访问 https://huggingface.co/settings/tokens
2. 登录或注册账号
3. 创建新的 Access Token（选择 Read 权限即可）
4. 复制 token（格式类似 `hf_xxxxxxxxxxxxxxxxxxxxx`）

---

## ✅ 验证配置

### 方法 1：查看客户端日志

大多数 MCP 客户端在设置中有"查看日志"功能，检查是否有连接错误。

### 方法 2：直接测试 Server

在命令行测试 Server 是否能启动：

```powershell
conda activate mcpserver
python E:\demoProject\speech_to_text\server.py
```

如果没有错误信息，按 `Ctrl+C` 退出，说明 Server 正常。

### 方法 3：使用 start_server.ps1

我们提供了启动脚本：

```powershell
cd E:\demoProject\speech_to_text
.\start_server.ps1
```

---

## 🛠️ 故障排查

### 问题 1：客户端无法连接

**原因：** 路径错误或 conda 环境未激活

**解决：**
1. 检查 `server.py` 的路径是否正确
2. 确保使用了 `conda run -n mcpserver`
3. 查看客户端日志中的具体错误信息

### 问题 2：连接后无法使用工具

**原因：** HUGGINGFACE_TOKEN 未设置或无效

**解决：**
1. 检查 token 是否正确（不要有多余空格）
2. 验证 token 是否有效：访问 https://huggingface.co/settings/tokens
3. 确保在配置中正确设置了环境变量

### 问题 3：转录失败

**原因：** FFmpeg 未安装或路径问题

**解决：**
```powershell
# 验证 FFmpeg 安装
ffmpeg -version

# 如果未安装
choco install ffmpeg
```

### 问题 4：说话人分离失败

**原因：** pyannote.audio 依赖问题

**解决：**
```powershell
conda activate mcpserver
pip install "numpy<2.0" --force-reinstall
pip install "pyannote.pipeline<4.0" --force-reinstall
```

---

## 📱 支持的客户端列表

以下客户端已测试支持 MCP：

✅ **Claude Desktop** - 官方客户端，推荐
✅ **Cherry Studio** - 开源多模型客户端
⚠️ **其他客户端** - 需要支持 MCP 协议

---

## 🎯 使用示例

配置成功后，你可以在 AI 客户端中这样使用：

### 示例 1：转录音频
```
请帮我转录这个音频文件：
C:\录音\会议.mp3
语言是中文
```

### 示例 2：带说话人分离
```
请转录这个会议录音，并识别不同的说话人：
C:\录音\团队讨论.mp3
```

### 示例 3：查询支持的格式
```
这个语音转文字工具支持哪些音频格式？
```

---

## 📞 需要帮助？

如果遇到问题：

1. 查看 `E:\demoProject\speech_to_text\PROJECT_SUMMARY.md`
2. 检查客户端日志文件
3. 确认所有依赖已正确安装

---

**配置时间：** 2025-11-18  
**Server 路径：** `E:\demoProject\speech_to_text\server.py`  
**Conda 环境：** `mcpserver`
