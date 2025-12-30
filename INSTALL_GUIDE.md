# 新手安装指南 (一步一步教程)

## 第一步: 安装 Python

1. 访问 Python 官网: https://www.python.org/downloads/
2. 下载 Python 3.10 或更高版本
3. 安装时 **务必勾选** "Add Python to PATH"
4. 验证安装:
   ```powershell
   python --version
   ```
   应该显示类似 `Python 3.11.x`

---

## 第二步: 创建虚拟环境

1. 打开 PowerShell
2. 进入项目目录:
   ```powershell
   cd e:\demoProject\speech_to_text
   ```

3. 创建虚拟环境:
   ```powershell
   python -m venv venv
   ```

4. 激活虚拟环境:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   **如果遇到权限错误:**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
   然后再次运行激活命令。

5. 验证虚拟环境已激活 (命令行前会显示 `(venv)`)

---

## 第三步: 安装 FFmpeg

FFmpeg 是音频处理必需的工具。

### 方法 1: 使用 Chocolatey (推荐)

1. 以管理员身份打开 PowerShell
2. 安装 Chocolatey:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```

3. 安装 FFmpeg:
   ```powershell
   choco install ffmpeg
   ```

4. 验证安装:
   ```powershell
   ffmpeg -version
   ```

### 方法 2: 手动安装

1. 访问: https://www.gyan.dev/ffmpeg/builds/
2. 下载 "ffmpeg-release-essentials.zip"
3. 解压到 `C:\ffmpeg`
4. 添加到系统 PATH:
   - 右键"此电脑" → "属性" → "高级系统设置"
   - "环境变量" → 找到 "Path" → "编辑"
   - "新建" → 输入 `C:\ffmpeg\bin`
   - 确定保存
5. 重启 PowerShell 并验证:
   ```powershell
   ffmpeg -version
   ```

---

## 第四步: 安装 Python 依赖包

1. 确保虚拟环境已激活 (看到 `(venv)` 前缀)

2. 安装项目:
   ```powershell
   pip install -e .
   ```

   这会安装所有需要的包:
   - mcp (MCP Server 框架)
   - openai-whisper (语音识别)
   - pyannote.audio (说话人分离)
   - torch (深度学习框架)
   - pydub (音频处理)
   等等...

3. 安装过程需要 5-15 分钟,请耐心等待

4. 验证安装:
   ```powershell
   python -c "import whisper; print('Whisper OK')"
   python -c "import torch; print('PyTorch OK')"
   ```

---

## 第五步: 获取 Hugging Face Token (说话人分离必需)

1. 访问 https://huggingface.co/ 并注册账号

2. 登录后访问: https://huggingface.co/settings/tokens

3. 点击 "New token" → 创建一个新 token → 复制保存

4. 接受模型使用协议:
   - 访问: https://huggingface.co/pyannote/speaker-diarization-3.1
   - 点击 "Agree and access repository"
   - 访问: https://huggingface.co/pyannote/segmentation-3.0
   - 点击 "Agree and access repository"

5. 设置环境变量 (临时,当前会话有效):
   ```powershell
   $env:HUGGINGFACE_TOKEN="hf_你的token"
   ```

   或永久设置:
   ```powershell
   [System.Environment]::SetEnvironmentVariable('HUGGINGFACE_TOKEN', 'hf_你的token', 'User')
   ```

---

## 第六步: 测试运行

### 本地测试 (不需要 MCP 客户端)

```powershell
python test_local.py
```

按提示操作:
1. 输入音频文件路径
2. 选择语言 (或留空自动检测)
3. 选择是否启用说话人分离
4. 等待处理完成

### 首次运行注意事项

第一次运行会下载模型文件:
- Whisper medium 模型: ~1.5GB
- Pyannote 模型: ~100MB

这是正常的,只需下载一次。

---

## 第七步: 配置 MCP 客户端

### 如果使用 Claude Desktop

1. 找到配置文件:
   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```

2. 编辑配置文件,添加:
   ```json
   {
     "mcpServers": {
       "speech-to-text": {
         "command": "python",
         "args": [
           "e:\\demoProject\\speech_to_text\\server.py"
         ],
         "env": {
           "HUGGINGFACE_TOKEN": "hf_你的token"
         }
       }
     }
   }
   ```

3. 重启 Claude Desktop

4. 在对话中使用工具

---

## 常见问题解决

### 问题 1: ModuleNotFoundError
**原因**: 虚拟环境未激活或依赖未安装  
**解决**:
```powershell
.\venv\Scripts\Activate.ps1
pip install -e .
```

### 问题 2: FFmpeg not found
**原因**: FFmpeg 未安装或不在 PATH 中  
**解决**: 重新按照第三步安装 FFmpeg

### 问题 3: CUDA out of memory
**原因**: GPU 内存不足  
**解决**: 使用 CPU 模式 (会自动检测并使用 CPU)

### 问题 4: Hugging Face authentication failed
**原因**: Token 未设置或未接受模型协议  
**解决**: 
1. 检查环境变量是否设置
2. 确认已接受模型使用协议

### 问题 5: 处理速度很慢
**原因**: 使用 CPU 而非 GPU  
**说明**: 这是正常的,CPU 模式会慢 3-5 倍,但仍可工作

---

## 下一步

阅读以下文档了解更多:
- `README.md` - 完整功能说明
- `EXAMPLES.md` - 使用示例
- 或直接运行 `python test_local.py` 开始使用!

---

## 需要帮助?

如果遇到问题:
1. 检查虚拟环境是否激活
2. 确认所有依赖已安装
3. 查看错误信息并根据上面的常见问题解决
4. 查看日志输出了解具体错误
