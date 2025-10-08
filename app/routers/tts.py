from fastapi import APIRouter, HTTPException, File, Form, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel
import logging
from ..services import tts_service

router = APIRouter()
logger = logging.getLogger(__name__)


class SimpleTTSRequest(BaseModel):
    text: str


@router.post("/text-to-speech/generate", tags=["Text to speech"])
async def simple_text_to_speech(request: SimpleTTSRequest):
    """
    Converts text to speech with default settings.
    Accepts a raw JSON body with only a 'text' field.
    """
    try:
        logger.info(f"Received TTS request for text: '{request.text}'")

        audio_bytes = tts_service.generate_simple_speech(text=request.text)

        if len(audio_bytes) == 0:
            raise HTTPException(status_code=500, detail="Generated audio is empty")

        logger.info(f"Returning audio with {len(audio_bytes)} bytes")

        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=speech.wav",
                "Content-Length": str(len(audio_bytes)),
            },
        )
    except Exception as e:
        logger.error(f"TTS generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text-to-speech/clone", tags=["Text to speech"])
async def clone_voice_text_to_speech(
    text: str = Form(
        ..., description="The new text to synthesize in the cloned voice."
    ),
    prompt_wav: UploadFile = File(
        ..., description="Prompt audio file (.wav) for voice cloning."
    ),
    prompt_text: str = Form(
        ..., description="The exact text transcription of the prompt audio."
    ),
):
    """
    Converts text to speech by cloning a voice from an uploaded audio file.
    Accepts multipart/form-data.
    """
    try:
        logger.info(f"Received voice cloning request for text: '{text}'")

        audio_bytes = tts_service.generate_cloned_speech(
            text=text, prompt_wav=prompt_wav, prompt_text=prompt_text
        )

        if len(audio_bytes) == 0:
            raise HTTPException(status_code=500, detail="Generated audio is empty")

        logger.info(f"Returning cloned audio with {len(audio_bytes)} bytes")

        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=cloned_speech.wav",
                "Content-Length": str(len(audio_bytes)),
            },
        )
    except Exception as e:
        logger.error(f"Voice cloning failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
