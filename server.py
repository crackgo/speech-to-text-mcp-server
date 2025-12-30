#!/usr/bin/env python3
"""
Speech-to-Text MCP Server
支持语音转文本和说话人分离功能
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional
import asyncio
import threading
from datetime import datetime

# 设置 FFmpeg 路径
if os.name == 'nt':  # Windows
    ffmpeg_path = r"C:\ProgramData\chocolatey\bin"
    if ffmpeg_path not in os.environ.get('PATH', ''):
        os.environ['PATH'] = ffmpeg_path + os.pathsep + os.environ.get('PATH', '')

# MCP imports
from mcp.server import Server
from mcp.types import Tool, TextContent

# 语音处理库
import whisper
import torch
import subprocess
import tempfile

# 延迟导入 pyannote.audio 以避免依赖冲突
# from pyannote.audio import Pipeline

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化 MCP Server
app = Server("speech-to-text-server")

# 全局变量存储模型
WHISPER_MODEL = None
DIARIZATION_PIPELINE = None

# 全局线程池,用于跟踪后台任务
BACKGROUND_THREADS = []

# 支持的音频格式
SUPPORTED_FORMATS = [
    "mp3", "wav", "m4a", "flac", "ogg", "wma", 
    "aac", "opus", "webm", "mp4"
]


def initialize_whisper_model(model_size: str = "medium"):
    """初始化 Whisper 模型"""
    global WHISPER_MODEL
    if WHISPER_MODEL is None:
        logger.info(f"正在加载 Whisper {model_size} 模型...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        WHISPER_MODEL = whisper.load_model(model_size, device=device)
        logger.info(f"Whisper 模型已加载到 {device}")
    return WHISPER_MODEL


def initialize_diarization_pipeline():
    """初始化说话人分离管道"""
    global DIARIZATION_PIPELINE
    if DIARIZATION_PIPELINE is None:
        # 延迟导入 pyannote.audio 以避免启动时的依赖冲突
        try:
            from pyannote.audio import Pipeline
        except ImportError as e:
            raise ImportError(
                "无法导入 pyannote.audio。请确保已安装所有依赖:\n"
                "pip install pyannote.audio torch torchvision torchaudio --upgrade\n"
                f"错误详情: {str(e)}"
            )
        
        hf_token = os.environ.get("HUGGINGFACE_TOKEN")
        if not hf_token:
            raise ValueError(
                "需要设置 HUGGINGFACE_TOKEN 环境变量来使用说话人分离功能。\n"
                "请访问 https://huggingface.co/settings/tokens 获取 token"
            )
        
        logger.info("正在加载说话人分离模型...")
        DIARIZATION_PIPELINE = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=hf_token
        )
        
        # 如果有 GPU,使用 GPU
        if torch.cuda.is_available():
            DIARIZATION_PIPELINE.to(torch.device("cuda"))
            logger.info("说话人分离模型已加载到 GPU")
        else:
            logger.info("说话人分离模型已加载到 CPU")
    
    return DIARIZATION_PIPELINE


def convert_to_wav(audio_path: str) -> str:
    """将音频文件转换为 WAV 格式"""
    audio_path_obj = Path(audio_path)
    
    # 如果已经是 WAV 格式,直接返回
    if audio_path_obj.suffix.lower() == '.wav':
        return audio_path
    
    logger.info(f"正在转换音频文件为 WAV 格式...")
    
    # 创建临时 WAV 文件
    wav_path = audio_path_obj.with_suffix('.wav')
    
    try:
        # 使用 ffmpeg 转换(设置编码避免中文路径问题)
        process = subprocess.Popen([
            'ffmpeg', '-i', str(audio_path),
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            '-y',  # 覆盖已存在文件
            str(wav_path)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', errors='ignore')
        
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, 'ffmpeg', stderr)
        
        logger.info(f"音频已转换为: {wav_path}")
        return str(wav_path)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"音频转换失败: {e}")


def get_audio_duration(audio_path: str) -> float:
    """获取音频时长(秒)"""
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(audio_path)
        ], capture_output=True, text=True, check=True, encoding='utf-8', errors='ignore')
        
        duration = float(result.stdout.strip())
        return duration
    except Exception as e:
        raise RuntimeError(f"无法获取音频时长: {e}")


def format_timestamp(seconds: float) -> str:
    """将秒数格式化为时间戳 HH:MM:SS.mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"


def transcribe_with_whisper(audio_path: str, language: Optional[str] = None) -> dict:
    """使用 Whisper 进行语音识别"""
    model = initialize_whisper_model()
    
    logger.info(f"开始转录音频: {audio_path}")
    
    # 转录参数
    transcribe_options = {
        "task": "transcribe",
        "verbose": False,
    }
    
    if language:
        transcribe_options["language"] = language
    
    # 执行转录
    result = model.transcribe(audio_path, **transcribe_options)
    
    logger.info("转录完成")
    return result


def perform_diarization(audio_path: str) -> dict:
    """执行说话人分离"""
    import time
    pipeline = initialize_diarization_pipeline()
    
    logger.info("开始说话人分离分析...")
    logger.info(f"音频文件: {audio_path}")
    
    # 确保音频是WAV格式（pyannote对WAV格式处理更稳定）
    if not audio_path.lower().endswith('.wav'):
        logger.info("转换音频为WAV格式以提高兼容性...")
        audio_path = convert_to_wav(audio_path)
        logger.info(f"已转换为: {audio_path}")
    
    # 获取音频时长用于进度估算
    duration = get_audio_duration(audio_path)
    logger.info(f"音频时长: {duration:.1f} 秒")
    
    # 执行分离（这一步可能需要很长时间）
    logger.info("正在执行 pyannote.audio 说话人分离（可能需要几分钟）...")
    start_time = time.time()
    
    try:
        # 对于长音频，pyannote可能会有tensor size不匹配的问题
        # 使用更小的batch size
        diarization = pipeline(audio_path)
        elapsed = time.time() - start_time
        logger.info(f"说话人分离完成，耗时: {elapsed:.1f} 秒")
    except RuntimeError as e:
        if "Sizes of tensors must match" in str(e):
            logger.warning(f"遇到tensor size问题，尝试重新处理: {e}")
            logger.info("使用备用处理方法...")
            # 重新加载pipeline可能会解决问题
            global DIARIZATION_PIPELINE
            DIARIZATION_PIPELINE = None
            pipeline = initialize_diarization_pipeline()
            diarization = pipeline(audio_path)
            elapsed = time.time() - start_time
            logger.info(f"说话人分离完成（备用方法），耗时: {elapsed:.1f} 秒")
        else:
            logger.error(f"说话人分离失败: {e}")
            raise
    except Exception as e:
        logger.error(f"说话人分离失败: {e}")
        raise
    
    # 将结果转换为字典格式
    speakers_timeline = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        speakers_timeline.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker
        })
    
    num_speakers = len(set(item['speaker'] for item in speakers_timeline))
    logger.info(f"识别到 {num_speakers} 个说话人，共 {len(speakers_timeline)} 个语音段")
    return speakers_timeline


def merge_transcription_with_diarization(transcription: dict, diarization: list) -> str:
    """将转录结果与说话人分离结果合并"""
    segments = transcription.get("segments", [])
    
    result_lines = []
    
    for segment in segments:
        start_time = segment["start"]
        end_time = segment["end"]
        text = segment["text"].strip()
        
        # 找到对应的说话人
        speaker = "UNKNOWN"
        for dia in diarization:
            # 如果转录片段的开始时间在说话人时间段内
            if dia["start"] <= start_time <= dia["end"]:
                speaker = dia["speaker"]
                break
        
        # 格式化输出
        timestamp = f"[{format_timestamp(start_time)} --> {format_timestamp(end_time)}]"
        line = f"[说话人 {speaker}] {timestamp}\n{text}\n"
        result_lines.append(line)
    
    return "\n".join(result_lines)


def format_simple_transcription(transcription: dict) -> str:
    """格式化简单转录结果(无说话人分离)"""
    segments = transcription.get("segments", [])
    
    result_lines = []
    for segment in segments:
        start_time = segment["start"]
        end_time = segment["end"]
        text = segment["text"].strip()
        
        timestamp = f"[{format_timestamp(start_time)} --> {format_timestamp(end_time)}]"
        line = f"{timestamp} {text}"
        result_lines.append(line)
    
    return "\n".join(result_lines)


def process_audio_in_background(
    audio_file_path: str,
    output_path: Path,
    language: Optional[str],
    enable_diarization: bool,
    duration_minutes: float
):
    """后台处理长音频文件并保存到文件"""
    
    # 立即创建处理标记文件
    marker_file = Path(output_path).with_suffix('.processing')
    try:
        with open(marker_file, 'w', encoding='utf-8') as f:
            f.write(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"音频文件: {audio_file_path}\n")
            f.write(f"线程ID: {threading.current_thread().name}\n")
    except Exception as e:
        logger.error(f"无法创建标记文件: {e}")
    
    # 立即记录线程启动
    logger.info("="*60)
    logger.info(f"🚀 后台线程已进入函数")
    logger.info(f"📁 处理文件: {audio_file_path}")
    logger.info(f"💾 输出路径: {output_path}")
    logger.info(f"⏱️ 音频时长: {duration_minutes:.1f} 分钟")
    logger.info("="*60)
    
    try:
        logger.info(f"🔄 开始转录处理...")
        
        # 转换为 WAV 格式
        wav_path = convert_to_wav(audio_file_path)
        
        # 执行转录
        transcription = transcribe_with_whisper(wav_path, language)
        
        # 如果启用说话人分离
        num_speakers = 0
        if enable_diarization:
            diarization = perform_diarization(wav_path)
            result_text = merge_transcription_with_diarization(transcription, diarization)
            num_speakers = len(set(seg["speaker"] for seg in diarization))
        else:
            result_text = format_simple_transcription(transcription)
        
        # 添加元信息
        detected_language = transcription.get("language", "unknown")
        header = f"{'='*60}\n"
        header += f"语音转录结果\n"
        header += f"{'='*60}\n\n"
        header += f"📁 文件: {Path(audio_file_path).name}\n"
        header += f"⏱️ 时长: {duration_minutes:.1f} 分钟\n"
        header += f"🌐 语言: {detected_language}\n"
        header += f"👥 说话人分离: {'已启用' if enable_diarization else '未启用'}\n"
        if enable_diarization and num_speakers > 0:
            header += f"🎤 识别说话人数: {num_speakers} 位\n"
        header += f"📅 转录时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"\n{'='*60}\n\n"
        
        full_result = header + result_text
        
        # 保存到文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_result)
        
        logger.info(f"✅ 后台任务完成: {output_path}")
        
        # 删除处理标记文件
        if marker_file.exists():
            marker_file.unlink()
        
    except Exception as e:
        error_msg = f"❌ 后台处理失败: {str(e)}\n"
        logger.error(error_msg, exc_info=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(error_msg)
        
        # 更新标记文件为错误状态
        try:
            with open(marker_file, 'a', encoding='utf-8') as f:
                f.write(f"\n错误时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"错误信息: {str(e)}\n")
        except:
            pass


async def transcribe_audio_file(
    audio_file_path: str,
    language: Optional[str] = "zh",
    enable_diarization: bool = True  # 默认开启说话人分离
) -> str:
    """
    转录音频文件 - 直接返回转录结果
    
    Args:
        audio_file_path: 音频文件路径
        language: 语言代码 (如 "zh", "en"),默认自动检测
        enable_diarization: 是否启用说话人分离
    
    Returns:
        完整的转录文本结果
    """
    try:
        # 验证文件存在
        if not Path(audio_file_path).exists():
            return f"❌ 错误: 文件不存在\n路径: {audio_file_path}"
        
        # 验证文件格式
        file_ext = Path(audio_file_path).suffix.lower().lstrip('.')
        if file_ext not in SUPPORTED_FORMATS:
            return f"❌ 错误: 不支持的文件格式 '{file_ext}'\n\n支持的格式: {', '.join(SUPPORTED_FORMATS)}"
        
        # 检查文件时长
        duration = get_audio_duration(audio_file_path)
        duration_minutes = duration / 60
        
        if duration_minutes > 60:
            return f"❌ 错误: 音频时长 {duration_minutes:.1f} 分钟超过 60 分钟限制"
        
        # 预估处理时间
        estimated_time = int(duration_minutes * 1.2)  # GPU 大约 1.2倍时间
        
        # 准备输出文件路径
        output_path = Path(audio_file_path).with_suffix('.txt')
        
        # 立即返回状态信息
        status_msg = f"""✅ 转录任务已启动！

📁 文件信息:
   - 文件名: {Path(audio_file_path).name}
   - 时长: {duration_minutes:.1f} 分钟
   - 格式: {file_ext.upper()}

⚙️ 处理设置:
   - 语言: {language or '自动检测'}
   - 说话人分离: {'是' if enable_diarization else '否'}
   - 设备: {'GPU (CUDA)' if torch.cuda.is_available() else 'CPU'}

⏱️ 预计时间: {estimated_time} 分钟

💾 结果将保存到:
   {output_path}

🔄 正在处理中，请稍候...
"""
        
        logger.info(f"开始转录: {audio_file_path}")
        logger.info(f"音频时长: {duration_minutes:.1f} 分钟，预计处理时间: {estimated_time} 分钟")
        
        # 根据音频长度决定处理方式
        # 短音频 (≤3分钟): 同步处理，直接返回完整结果
        # 长音频 (>3分钟): 立即返回状态，后台处理并保存到文件
        
        if duration_minutes <= 3:
            # 短音频 - 同步处理并直接返回
            logger.info("🎯 短音频，同步处理中...")
            
            # 转换为 WAV 格式
            wav_path = convert_to_wav(audio_file_path)
            
            # 执行转录
            transcription = transcribe_with_whisper(wav_path, language)
            
            # 如果启用说话人分离
            num_speakers = 0
            if enable_diarization:
                diarization = perform_diarization(wav_path)
                result_text = merge_transcription_with_diarization(transcription, diarization)
                num_speakers = len(set(seg["speaker"] for seg in diarization))
            else:
                result_text = format_simple_transcription(transcription)
            
            # 添加元信息
            detected_language = transcription.get("language", "unknown")
            header = f"{'='*60}\n"
            header += f"语音转录结果\n"
            header += f"{'='*60}\n\n"
            header += f"📁 文件: {Path(audio_file_path).name}\n"
            header += f"⏱️ 时长: {duration_minutes:.1f} 分钟\n"
            header += f"🌐 语言: {detected_language}\n"
            header += f"👥 说话人分离: {'已启用' if enable_diarization else '未启用'}\n"
            if enable_diarization and num_speakers > 0:
                header += f"🎤 识别说话人数: {num_speakers} 位\n"
            header += f"📅 转录时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            header += f"\n{'='*60}\n\n"
            
            full_result = header + result_text
            
            logger.info(f"✅ 转录完成")
            
            # 清理临时文件
            if wav_path != audio_file_path and os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                except:
                    pass
            
            # 直接返回完整结果
            return full_result
            
        else:
            # 长音频 - 使用独立进程处理,避免MCP超时
            logger.info("📁 长音频,使用独立进程处理...")
            
            # 准备独立进程的日志文件
            log_file = output_path.with_suffix('.log')
            stderr_file = output_path.with_suffix('.stderr')
            
            # 使用subprocess启动独立Python进程
            import subprocess
            python_exe = sys.executable  # 使用当前Python解释器
            script_path = Path(__file__).parent / "standalone_transcribe.py"
            
            # 复制当前环境变量,确保HUGGINGFACE_TOKEN等被传递
            env = os.environ.copy()
            
            # Windows平台使用CREATE_NO_WINDOW创建后台进程
            if os.name == 'nt':
                import subprocess
                CREATE_NO_WINDOW = 0x08000000
                creation_flags = CREATE_NO_WINDOW
            else:
                creation_flags = 0
            
            # 启动独立进程
            process = subprocess.Popen(
                [
                    python_exe,
                    "-u",  # 无缓冲输出
                    str(script_path),
                    audio_file_path,
                    str(output_path),
                    language or "None",
                    str(enable_diarization),
                    str(log_file)
                ],
                env=env,  # 传递环境变量
                stdout=open(stderr_file, 'w', encoding='utf-8', buffering=1),
                stderr=subprocess.STDOUT,  # 合并stderr到stdout
                creationflags=creation_flags
            )
            
            logger.info(f"独立进程已启动: PID={process.pid}")
            logger.info(f"日志文件: {log_file}")
            logger.info(f"错误日志: {stderr_file}")
            
            # 立即返回任务信息
            return f"""✅ 转录任务已在独立进程中启动

📁 文件信息:
   - 文件名: {Path(audio_file_path).name}
   - 时长: {duration_minutes:.1f} 分钟
   - 格式: {file_ext.upper()}

⚙️ 处理设置:
   - 语言: {language or '自动检测'}
   - 说话人分离: {'是' if enable_diarization else '否'}
   - 设备: {'GPU (CUDA)' if torch.cuda.is_available() else 'CPU'}
   - 进程ID: {process.pid}

⏱️ 预计完成时间: 约 {estimated_time} 分钟后

💾 结果将保存到:
   {output_path}

📋 查看处理进度:
   日志文件: {log_file}
   错误日志: {stderr_file}

🔄 处理将在独立进程中完成,不受MCP超时限制。
完成后请打开输出文件查看转录结果。
"""
        
    except Exception as e:
        error_msg = f"❌ 转录失败: {str(e)}\n\n详细错误信息请查看日志"
        logger.error(error_msg, exc_info=True)
        return error_msg


# 定义 MCP 工具
@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用工具"""
    return [
        Tool(
            name="transcribe_audio",
            description=(
                "将音频文件转录为文本。"
                "短音频(≤5分钟)直接返回完整结果；"
                "长音频(>5分钟)后台处理并保存到同名.txt文件(避免MCP超时)。"
                "默认启用说话人分离功能，支持识别不同说话人。"
                "处理时间约为音频时长的1.2倍（GPU加速）。"
                "支持格式: mp3, wav, m4a, flac, ogg, wma 等。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "audio_file_path": {
                        "type": "string",
                        "description": "音频文件的完整路径 (例如: C:\\Users\\username\\audio.mp3)"
                    },
                    "language": {
                        "type": "string",
                        "description": "语言代码,如 'zh' (中文), 'en' (英文), 'ja' (日语)。留空则自动检测",
                        "default": "zh"
                    },
                    "enable_diarization": {
                        "type": "boolean",
                        "description": "是否启用说话人分离(识别不同说话人),需要 HUGGINGFACE_TOKEN",
                        "default": True
                    }
                },
                "required": ["audio_file_path"]
            }
        ),
        Tool(
            name="get_supported_formats",
            description="获取支持的音频格式列表",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """处理工具调用"""
    
    try:
        if name == "transcribe_audio":
            audio_file_path = arguments.get("audio_file_path")
            language = arguments.get("language")
            enable_diarization = arguments.get("enable_diarization", True)
            
            if not audio_file_path:
                return [TextContent(
                    type="text",
                    text="错误: 缺少必需参数 'audio_file_path'"
                )]
            
            result = await transcribe_audio_file(
                audio_file_path=audio_file_path,
                language=language,
                enable_diarization=enable_diarization
            )
            
            return [TextContent(type="text", text=result)]
        
        elif name == "get_supported_formats":
            formats_text = "支持的音频格式:\n" + "\n".join(f"- {fmt}" for fmt in SUPPORTED_FORMATS)
            return [TextContent(type="text", text=formats_text)]
        
        else:
            return [TextContent(type="text", text=f"未知工具: {name}")]
    
    except Exception as e:
        error_message = f"工具执行错误: {str(e)}"
        logger.error(error_message, exc_info=True)
        return [TextContent(type="text", text=error_message)]


async def main():
    """主函数"""
    # 使用 stdio 传输运行服务器
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Speech-to-Text MCP Server 已启动")
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
