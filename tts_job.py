# tts_job.py
import subprocess
import logging
from pathlib import Path
import uuid
import os

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_tts_command(text, voice="random", preset="fast", output_dir="output"):
    """
    Execute TTS command with the given parameters
    
    Args:
        text (str): Text to convert to speech
        voice (str): Voice to use (default: random)
        preset (str): Preset to use (default: fast)
        output_dir (str): Directory to save output files
    
    Returns:
        dict: Result containing status and output file path
    """
    try:
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        output_file = f"{output_dir}/tts_{uuid.uuid4()}.wav"
        
        # Construct the command
        cmd = [
            "python",
            "tortoise/do_tts.py",
            "--text",
            text,
            "--voice",
            voice,
            "--preset",
            preset,
            "--output_path",
            output_file
        ]
        
        logger.info(f"Executing command: {' '.join(cmd)}")
        
        # Execute the command
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Get output and errors
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            logger.info("TTS command executed successfully")
            return {
                "status": "success",
                "output_file": output_file,
                "stdout": stdout,
                "stderr": stderr
            }
        else:
            logger.error(f"TTS command failed: {stderr}")
            return {
                "status": "error",
                "error": stderr,
                "stdout": stdout
            }
            
    except Exception as e:
        logger.error(f"Error executing TTS command: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }