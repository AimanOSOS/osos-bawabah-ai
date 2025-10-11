from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
import tempfile
import os
import logging
from ..services import stt_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/speech-to-text/generate", tags=["Speech to text"])
async def speech_to_text(
    audio_file: UploadFile = File(..., description="Audio file for transcription"),
):
    """
    Converts speech to text using Whisper Large model with detailed output.
    """
    temp_file_path = None
    try:
        logger.info(f"Received STT request for file: '{audio_file.filename}'")

        # Validate file type
        if not audio_file.content_type or not audio_file.content_type.startswith(
            "audio/"
        ):
            raise HTTPException(status_code=400, detail="File must be an audio file")

        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Transcribe audio
        results = stt_service.transcribe_audio(temp_file_path)

        # Return the results directly (not wrapped in another dict)
        return JSONResponse(content=results)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"STT generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to remove temp file {temp_file_path}: {e}")
