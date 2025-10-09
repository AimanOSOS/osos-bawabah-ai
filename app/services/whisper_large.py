from .model_loader import get_audio_to_text_model
import logging
import librosa

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def chunk_audio(audio_file) -> list[str]:
    """Chunks audio into 30 second segments."""
    y, sr = librosa.load(audio_file, sr=16000)
    segments = librosa.util.frame(y, frame_length=sr * 30, hop_length=sr * 15)
    return segments

def transcribe_audio(audio_file) -> str:
    """Transcribes audio to text using Whisper model."""
    model = get_audio_to_text_model()
    result = model.transcribe(audio_file)
    logger.info(f"Transcribed audio to text: {result['text']}")
    return result["text"]
