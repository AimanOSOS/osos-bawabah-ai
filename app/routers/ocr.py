from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from io import BytesIO
from PIL import Image
from pydantic import BaseModel, Field
from typing import List, Optional

from app.services.dolphin_ocr_service import DolphinOCRService

router = APIRouter(tags=["Dolphin OCR"])

# Define response models
class OCRBlock(BaseModel):
    text: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.99)
    bbox: Optional[List[int]] = None
    element_type: Optional[str] = None

class OCRResponse(BaseModel):
    text: str
    markdown: str
    blocks: List[OCRBlock] = []
    model_id: str
    took_ms: int


@router.post("/ocr/dolphin", response_model=OCRResponse)
async def dolphin_ocr(
    file: UploadFile = File(...),
    return_blocks: bool = Form(True),
    language_hint: str | None = Form(None),
):
    """Extract text from image using Dolphin OCR and return markdown text."""
    try:
        data = await file.read()
        image = Image.open(BytesIO(data)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {e}")

    try:
        result = DolphinOCRService.run(
            image=image,
            return_blocks=return_blocks,
            language_hint=language_hint,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {e}")
