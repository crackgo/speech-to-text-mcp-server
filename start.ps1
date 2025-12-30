# 快速启动脚本 - 启动 MCP Server

Write-Host "启动 Speech-to-Text MCP Server..." -ForegroundColor Cyan

# 检查虚拟环境
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "错误: 虚拟环境未找到,请先运行 setup.ps1" -ForegroundColor Red
    exit 1
}

# 检查环境变量
if (-not $env:HUGGINGFACE_TOKEN) {
    Write-Host "警告: HUGGINGFACE_TOKEN 未设置" -ForegroundColor Yellow
    Write-Host "说话人分离功能将不可用" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "设置方法:" -ForegroundColor Cyan
    Write-Host '  $env:HUGGINGFACE_TOKEN="hf_你的token"' -ForegroundColor White
    Write-Host ""
}

# 激活虚拟环境并启动
.\venv\Scripts\Activate.ps1
Write-Host "MCP Server 正在运行..." -ForegroundColor Green
Write-Host "按 Ctrl+C 停止服务器" -ForegroundColor Yellow
Write-Host ""

python server.py
