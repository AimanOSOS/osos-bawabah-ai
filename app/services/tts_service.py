import soundfile as sf
import io
import tempfile
import os
import logging
from fastapi import UploadFile
from .model_loader import get_tts_model
from ..config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_simple_speech(text: str) -> bytes:
    """Generates speech using optimized model settings."""
    model = get_tts_model()
    
    # Preprocess text to avoid issues with very short or problematic inputs
    text = text.strip()
    if len(text) < 3:
        text = text + "."  # Add punctuation for very short texts
    
    logger.info(f"Generating speech for text: '{text}' (length: {len(text)})")
    
    try:
        wav_data = model.generate(
            text=text,
            prompt_wav_path=None,      # No voice cloning for simple TTS
            prompt_text=None,          # No reference text for simple TTS
            cfg_value=settings.default_cfg_value,             # LM guidance on LocDiT, higher for better adherence
            inference_timesteps=settings.default_inference_timesteps,    # Reduced from 20 for faster generation
            normalize=True,            # Enable external TN tool
            denoise=True,              # Enable external Denoise tool
            retry_badcase=True,        # Enable retrying mode for bad cases
            retry_badcase_max_times=settings.default_retry_max_times, # Maximum retrying times
            retry_badcase_ratio_threshold=settings.default_retry_ratio_threshold  # Maximum length restriction for bad case detection
        )
        
        logger.info(f"Generated audio data shape: {wav_data.shape if hasattr(wav_data, 'shape') else 'unknown'}")
        
        # Create audio buffer
        buffer = io.BytesIO()
        sf.write(buffer, wav_data, settings.sample_rate, format=settings.audio_format)
        buffer.seek(0)
        audio_bytes = buffer.read()
        
        logger.info(f"Generated audio bytes length: {len(audio_bytes)}")
        
        return audio_bytes
        
    except Exception as e:
        logger.error(f"Error generating speech: {str(e)}")
        raise


def generate_cloned_speech(text: str, prompt_wav: UploadFile, prompt_text: str) -> bytes:
    """Generates speech by cloning the voice from a prompt audio file."""
    model = get_tts_model()
    
    # Preprocess text
    text = text.strip()
    if len(text) < 3:
        text = text + "."
    
    logger.info(f"Generating cloned speech for text: '{text}' (length: {len(text)})")
    
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(prompt_wav.file.read())
            temp_file_path = temp_file.name

        wav_data = model.generate(
            text=text,
            prompt_wav_path=temp_file_path,  # Path to prompt audio for voice cloning
            prompt_text=prompt_text,         # Reference text for voice cloning
            cfg_value=settings.default_cfg_value,                  # LM guidance on LocDiT
            inference_timesteps=settings.default_inference_timesteps,         # LocDiT inference timesteps
            normalize=True,                 # Enable external TN tool
            denoise=True,                   # Enable external Denoise tool
            retry_badcase=True,             # Enable retrying mode for bad cases
            retry_badcase_max_times=settings.default_retry_max_times,      # Maximum retrying times
            retry_badcase_ratio_threshold=settings.default_retry_ratio_threshold  # Maximum length restriction for bad case detection
        )
        
        logger.info(f"Generated cloned audio data shape: {wav_data.shape if hasattr(wav_data, 'shape') else 'unknown'}")
        
        buffer = io.BytesIO()
        sf.write(buffer, wav_data, settings.sample_rate, format=settings.audio_format) 
        buffer.seek(0)
        audio_bytes = buffer.read()
        
        logger.info(f"Generated cloned audio bytes length: {len(audio_bytes)}")
        
        return audio_bytes

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)