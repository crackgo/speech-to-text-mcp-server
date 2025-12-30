# 自动安装脚本 - Windows PowerShell
# 运行此脚本自动完成环境配置

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Speech-to-Text MCP Server 安装向导" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python
Write-Host "步骤 1/5: 检查 Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ 找到 Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ 未找到 Python,请先安装 Python 3.10+" -ForegroundColor Red
    Write-Host "下载地址: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# 创建虚拟环境
Write-Host ""
Write-Host "步骤 2/5: 创建虚拟环境..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✓ 虚拟环境已存在" -ForegroundColor Green
} else {
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 虚拟环境创建成功" -ForegroundColor Green
    } else {
        Write-Host "✗ 虚拟环境创建失败" -ForegroundColor Red
        exit 1
    }
}

# 激活虚拟环境
Write-Host ""
Write-Host "步骤 3/5: 激活虚拟环境..." -ForegroundColor Yellow
try {
    .\venv\Scripts\Activate.ps1
    Write-Host "✓ 虚拟环境已激活" -ForegroundColor Green
} catch {
    Write-Host "✗ 激活失败,尝试修改执行策略..." -ForegroundColor Yellow
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    .\venv\Scripts\Activate.ps1
    Write-Host "✓ 虚拟环境已激活" -ForegroundColor Green
}

# 升级 pip
Write-Host ""
Write-Host "步骤 4/5: 升级 pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
Write-Host "✓ pip 已升级" -ForegroundColor Green

# 安装依赖
Write-Host ""
Write-Host "步骤 5/5: 安装依赖包..." -ForegroundColor Yellow
Write-Host "这可能需要 10-15 分钟,请耐心等待..." -ForegroundColor Cyan
pip install -e .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ 依赖安装成功!" -ForegroundColor Green
} else {
    Write-Host "✗ 依赖安装失败" -ForegroundColor Red
    exit 1
}

# 检查 FFmpeg
Write-Host ""
Write-Host "检查 FFmpeg..." -ForegroundColor Yellow
try {
    $ffmpegVersion = ffmpeg -version 2>&1 | Select-Object -First 1
    Write-Host "✓ FFmpeg 已安装: $ffmpegVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠ 未找到 FFmpeg" -ForegroundColor Yellow
    Write-Host "请安装 FFmpeg:" -ForegroundColor Yellow
    Write-Host "  方法 1: choco install ffmpeg" -ForegroundColor Cyan
    Write-Host "  方法 2: 手动下载 https://ffmpeg.org/" -ForegroundColor Cyan
}

# 完成
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "安装完成!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步:" -ForegroundColor Yellow
Write-Host "1. 获取 Hugging Face Token (用于说话人分离)" -ForegroundColor White
Write-Host "   访问: https://huggingface.co/settings/tokens" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. 设置环境变量:" -ForegroundColor White
Write-Host "   `$env:HUGGINGFACE_TOKEN='hf_你的token'" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. 运行测试:" -ForegroundColor White
Write-Host "   python test_local.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "查看完整文档: INSTALL_GUIDE.md" -ForegroundColor Yellow
Write-Host ""
