from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
import logging
from ..services import itx_service

router = APIRouter()
logger = logging.getLogger(__name__)


class ImageToTextResponse(BaseModel):
    description: str


@router.post("/image-to-text/generate", tags=["Image to Text"])
async def image_to_text(
    image: UploadFile = File(..., description="Image file for caption generation"),
    prompt: str = Form("Describe this image.", description="Prompt for guidance"),
):
    """
    Converts an image into descriptive text using IBM Granite Vision 3.2-2B.
    """
    try:
        description = itx_service.generate_image_description(image, prompt)
        return {"description": description}
    except Exception as e:
        logger.error(f"Image-to-text generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
