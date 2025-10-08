import io
import logging
from PIL import Image
from fastapi import UploadFile
from .model_loader import get_granite_vision_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_image_description(
    image_file: UploadFile, prompt: str = "Describe this image."
) -> str:
    """Generates a textual description from an image using IBM Granite Vision 3.2-2B."""
    model, processor = get_granite_vision_model()

    try:
        image_data = image_file.file.read()
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        logger.info(f"Processing image: {image_file.filename}")

        inputs = processor(prompt, image, return_tensors="pt").to(model.device)
        outputs = model.generate(**inputs, max_new_tokens=128)
        text = processor.decode(outputs[0], skip_special_tokens=True)

        logger.info(f"Generated description: {text}")
        return text

    except Exception as e:
        logger.error(f"Error generating image description: {str(e)}")
        raise
