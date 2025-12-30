"""
独立进程转录脚本
由MCP服务器调用,在独立进程中运行
"""
import sys
import os
from pathlib import Path
import logging
from datetime import datetime

def main():
    """主函数"""
    
    # 首先设置基础日志(先输出到stderr)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )
    logger = logging.getLogger(__name__)
    
    logger.info("="*60)
    logger.info("独立转录进程启动")
    logger.info(f"Python: {sys.version}")
    logger.info(f"参数数量: {len(sys.argv)}")
    logger.info(f"参数列表: {sys.argv}")
    logger.info("="*60)
    
    if len(sys.argv) < 5:
        logger.error("参数不足")
        logger.error("用法: python standalone_transcribe.py <audio_file> <output_file> <language> <enable_diarization> [log_file]")
        sys.exit(1)
    
    audio_file_path = sys.argv[1]
    output_path = sys.argv[2]
    language = sys.argv[3] if sys.argv[3] != "None" else None
    enable_diarization = sys.argv[4].lower() == "true"
    
    # 设置日志文件
    if len(sys.argv) > 5:
        log_file = Path(sys.argv[5])
        # 重新配置日志,同时输出到文件和stderr
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8', mode='w'),
                logging.StreamHandler(sys.stderr)
            ]
        )
        logger = logging.getLogger(__name__)
        logger.info("日志文件已配置: " + str(log_file))
    
    logger.info("="*60)
    logger.info("独立进程转录任务")
    logger.info("="*60)
    logger.info(f"音频文件: {audio_file_path}")
    logger.info(f"输出文件: {output_path}")
    logger.info(f"语言: {language}")
    logger.info(f"说话人分离: {enable_diarization}")
    logger.info("="*60)
    
    # 创建处理标记文件
    marker_file = Path(output_path).with_suffix('.processing')
    try:
        with open(marker_file, 'w', encoding='utf-8') as f:
            f.write(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"音频文件: {audio_file_path}\n")
            f.write(f"进程ID: {os.getpid()}\n")
    except Exception as e:
        logger.error(f"无法创建标记文件: {e}")
    
    try:
        # 导入处理函数
        sys.path.insert(0, str(Path(__file__).parent))
        from server import (
            convert_to_wav,
            transcribe_with_whisper,
            perform_diarization,
            merge_transcription_with_diarization,
            format_simple_transcription,
            get_audio_duration
        )
        
        # 获取时长
        duration = get_audio_duration(audio_file_path)
        duration_minutes = duration / 60
        
        logger.info(f"音频时长: {duration_minutes:.1f} 分钟")
        
        # 转换为WAV
        logger.info("转换为WAV格式...")
        wav_path = convert_to_wav(audio_file_path)
        
        # 执行转录
        logger.info("开始Whisper转录...")
        transcription = transcribe_with_whisper(wav_path, language)
        logger.info(f"转录完成,片段数: {len(transcription.get('segments', []))}")
        
        # 如果启用说话人分离
        num_speakers = 0
        if enable_diarization:
            logger.info("开始说话人分离...")
            diarization = perform_diarization(wav_path)
            result_text = merge_transcription_with_diarization(transcription, diarization)
            num_speakers = len(set(seg["speaker"] for seg in diarization))
            logger.info(f"说话人分离完成,识别 {num_speakers} 位说话人")
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
        
        logger.info(f"✅ 转录完成: {output_path}")
        logger.info(f"文件大小: {os.path.getsize(output_path) / 1024:.2f} KB")
        
        # 删除标记文件
        if marker_file.exists():
            marker_file.unlink()
            logger.info("已删除处理标记文件")
        
    except Exception as e:
        logger.error(f"❌ 处理失败: {str(e)}", exc_info=True)
        
        # 写入错误信息到输出文件
        error_msg = f"❌ 转录失败\n\n错误信息: {str(e)}\n"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(error_msg)
        
        # 更新标记文件
        try:
            with open(marker_file, 'a', encoding='utf-8') as f:
                f.write(f"\n错误时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"错误信息: {str(e)}\n")
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()
