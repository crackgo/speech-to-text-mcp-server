# 语音转文字工具 - 使用指南

## ✅ MCP Server 已成功连接！

恭喜！你的 MCP Server 已经可以和 360 脑图 AI / Cherry Studio 通信了！

但是有一个**重要限制**：
- 音频转录需要较长时间（16分钟音频需要约19分钟处理）
- MCP 客户端通常有 **30-60秒的超时限制**
- 因此会出现 "Request timed out" 错误

---

## 🎯 推荐使用方式

### 方案一：使用命令行工具（最稳定）⭐

**1. 快速转录（无说话人分离）**
```powershell
conda activate mcpserver
python E:\demoProject\speech_to_text\quick_test.py "C:\Users\huang\Desktop\新建文件夹\面试考题素材_会议录音.MP3" zh
```

**2. 带说话人分离的转录**
```powershell
conda activate mcpserver
python E:\demoProject\speech_to_text\diarize_test.py "C:\Users\huang\Desktop\新建文件夹\面试考题素材_会议录音.MP3" zh
```

**特点：**
- ✅ 无超时限制
- ✅ 显示实时进度
- ✅ 自动保存结果到 .txt 文件
- ✅ 可以处理长达 60 分钟的音频

---

### 方案二：通过 AI 助手调用（适合短音频）

MCP Server 可以正常工作，但**仅适合处理短音频**（<3分钟）。

**使用步骤：**

1. 在 360 脑图 AI 或 Cherry Studio 中提问：
   ```
   请帮我转录这个音频文件：
   C:\Users\huang\Desktop\短音频.mp3
   使用中文
   ```

2. AI 会调用 `transcribe_audio` 工具

3. **如果音频较长**（>3分钟），会出现超时错误，这是正常的！

**解决方案：** 使用命令行工具处理长音频

---

## 📊 处理时间参考

| 音频时长 | GPU 处理时间 | 是否适合 MCP |
|---------|-------------|-------------|
| 1 分钟 | ~1.2 分钟 | ✅ 适合 |
| 3 分钟 | ~3.6 分钟 | ⚠️ 可能超时 |
| 5 分钟 | ~6 分钟 | ❌ 会超时 |
| 16 分钟 | ~19 分钟 | ❌ 必须用命令行 |

---

## 🔧 Cherry Studio 配置确认

你的配置是正确的：

| 字段 | 值 |
|------|-----|
| 命令 | `E:\Anaconda3\envs\mcpserver\python.exe` |
| 参数 | `E:\demoProject\speech_to_text\server.py` |
| 环境变量 | `HUGGINGFACE_TOKEN=hf_...` |

**验证方法：**
看到这个错误说明连接成功：
```
Error calling tool transcribe_audio: 
MCP error -32001: Request timed out
```

这**不是配置错误**，而是处理时间过长导致的超时。

---

## 💡 智能使用建议

### 场景 1：会议录音（16分钟）
**推荐：** 命令行工具
```powershell
conda activate mcpserver
python diarize_test.py "会议录音.mp3" zh
```
等待 20 分钟，自动保存完整转录和说话人分离结果。

### 场景 2：语音备忘录（1-2分钟）
**推荐：** 通过 AI 助手
在 360 脑图 AI 中直接问：
```
帮我转录这个语音备忘录：备忘录.mp3，中文
```

### 场景 3：批量处理
**推荐：** 批处理脚本
```powershell
conda activate mcpserver
python batch_transcribe.py "E:\音频文件夹" zh
```

---

## 📝 完整示例

### 你的测试文件

**文件：** `C:\Users\huang\Desktop\新建文件夹\面试考题素材_会议录音.MP3`
**时长：** 16.2 分钟
**处理时间：** ~19 分钟（GPU）

**命令：**
```powershell
conda activate mcpserver
cd E:\demoProject\speech_to_text
python diarize_test.py "C:\Users\huang\Desktop\新建文件夹\面试考题素材_会议录音.MP3" zh
```

**输出：**
- 屏幕显示处理进度
- 自动识别说话人（SPEAKER_01, SPEAKER_02, ...）
- 保存结果到：`C:\Users\huang\Desktop\新建文件夹\面试考题素材_会议录音.txt`

---

## 🚀 快速启动命令

**创建桌面快捷方式：**

1. 创建文件 `转录音频.bat`：
```batch
@echo off
cd /d E:\demoProject\speech_to_text
call conda activate mcpserver
echo.
echo ========================================
echo 语音转文字工具
echo ========================================
echo.
set /p audio_path="请输入音频文件路径: "
set /p language="请输入语言代码(zh/en/ja，直接回车=zh): "
if "%language%"=="" set language=zh
echo.
echo 是否启用说话人分离？
set /p diarize="输入 y 启用，其他键跳过: "
if /i "%diarize%"=="y" (
    python diarize_test.py "%audio_path%" %language%
) else (
    python quick_test.py "%audio_path%" %language%
)
pause
```

2. 双击运行，输入文件路径即可！

---

## ✅ 总结

1. **MCP Server 配置成功** ✅
2. **适合场景：** 短音频（<3分钟）通过 AI 助手调用
3. **长音频推荐：** 使用命令行工具
4. **你的会议录音：** 使用 `diarize_test.py` 处理

需要我帮你运行转录命令吗？
