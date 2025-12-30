@echo off
REM MCP Server 启动脚本（用于 360 脑图 AI）
REM 此脚本会记录启动日志以便调试

echo Starting Speech-to-Text MCP Server... > mcp_server.log
echo Time: %date% %time% >> mcp_server.log
echo. >> mcp_server.log

REM 设置环境变量
set HUGGINGFACE_TOKEN=hf_JmsDHt-ERbTfSpdLumZaMx-Qd8r8CAKcVcS

REM 启动 server
E:\Anaconda3\envs\mcpserver\python.exe E:\demoProject\speech_to_text\server.py 2>> mcp_server.log

echo Server stopped at %time% >> mcp_server.log
