from fastapi import APIRouter, File, UploadFile, Form, HTTPException, BackgroundTasks
from pydantic import BaseModel
import logging
from starlette.concurrency import run_in_threadpool
from ..services import image_to_text_service

router = APIRouter()
logger = logging.getLogger(__name__)


class ImageToTextResponse(BaseModel):
    description: str


@router.post(
    "/image-to-text/generate",
    tags=["Image to Text"],
    response_model=ImageToTextResponse,
)
async def image_to_text(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(..., description="Image file for caption generation"),
    prompt: str = Form(
        "Describe this image in detail.", description="Prompt for guidance"
    ),
):
    """
    Converts an image into descriptive text using IBM Granite Vision 3.2-2B.
    """
    try:
        # Run in background to avoid blocking event loop (model is heavy)
        description = await run_in_threadpool(
            image_to_text_service.generate_image_description, image, prompt
        )

        return {"description": description}

    except Exception as e:
        logger.error(f"Image-to-text generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
