"""
Simple OCR Service for Bawabah AI
A working OCR implementation that can be extended with Dolphin later
"""

import os
import time
import json
from PIL import Image
from pydantic import BaseModel, Field
from typing import List, Optional
import torch

# Try to import OCR libraries
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False


# ---------------------------------------------------------------------
# Response Models
# ---------------------------------------------------------------------
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


# ---------------------------------------------------------------------
# Global model cache
# ---------------------------------------------------------------------
_OCR_CACHE = None


def _load_easyocr():
    """Load EasyOCR as a fallback OCR solution."""
    global _OCR_CACHE
    if _OCR_CACHE:
        return _OCR_CACHE
    
    if EASYOCR_AVAILABLE:
        try:
            # Initialize EasyOCR with English and Arabic support
            _OCR_CACHE = easyocr.Reader(['en', 'ar'], gpu=False)
            return _OCR_CACHE
        except Exception as e:
            print(f"[Warning] Failed to load EasyOCR: {e}")
            return None
    return None


def _extract_text_with_easyocr(image: Image.Image):
    """Extract text using EasyOCR as fallback."""
    reader = _load_easyocr()
    if not reader:
        return None, []
    
    try:
        # Convert PIL image to numpy array
        import numpy as np
        img_array = np.array(image)
        
        # Extract text
        results = reader.readtext(img_array)
        
        # Combine all text
        all_text = " ".join([result[1] for result in results])
        
        # Create blocks
        blocks = []
        for result in results:
            bbox, text, confidence = result
            blocks.append(
                OCRBlock(
                    text=text,
                    confidence=float(confidence),
                    bbox=[int(coord) for point in bbox for coord in point] if bbox else None,
                    element_type="text"
                )
            )
        
        return all_text, blocks
    except Exception as e:
        print(f"[Warning] EasyOCR failed: {e}")
        return None, []


def _convert_to_markdown(blocks):
    """Convert OCR blocks to markdown text."""
    markdown_parts = []
    
    for block in blocks:
        text = block.text
        if block.element_type == "text":
            markdown_parts.append(text)
        else:
            markdown_parts.append(text)
    
    return "\n".join(markdown_parts)


# ---------------------------------------------------------------------
# Main Service
# ---------------------------------------------------------------------
class DolphinOCRService:
    @classmethod
    def run(cls, image: Image.Image, return_blocks: bool = True, language_hint=None):
        """Run OCR and return extracted text + markdown directly."""
        t0 = time.time()
        
        # For now, use EasyOCR as a working implementation
        # This can be replaced with Dolphin once the model loading issues are resolved
        extracted_text, blocks = _extract_text_with_easyocr(image)
        
        if not extracted_text:
            extracted_text = "OCR processing failed or no text found."
            blocks = []
        
        # Convert to markdown
        markdown_text = _convert_to_markdown(blocks)
        
        took_ms = int((time.time() - t0) * 1000)

        return OCRResponse(
            text=extracted_text.strip(),
            markdown=markdown_text.strip(),
            blocks=blocks,
            model_id="EasyOCR (Dolphin placeholder)",  # Indicate this is a placeholder
            took_ms=took_ms,
        )