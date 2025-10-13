import io
import logging
from PIL import Image
from fastapi import UploadFile
from .model_loader import get_granite_vision_model
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_image_description(
    image_file: UploadFile, prompt: str = "Describe this image in detail."
) -> str:
    """Generates a textual description from an image using IBM Granite Vision 3.2-2B."""
    model, processor = get_granite_vision_model()

    try:
        # Read image
        image_data = image_file.file.read()
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        logger.info(f"Processing image: {image_file.filename}")

        # Step 1: Build conversation
        conversation = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": prompt},
                ],
            },
        ]

        # Step 2: Create text template (string)
        prompt_text = processor.apply_chat_template(
            conversation,
            add_generation_prompt=True,
            tokenize=False,  # return string, not tensor
        )

        # Step 3: Tokenize + include image
        inputs = processor(text=prompt_text, images=image, return_tensors="pt").to(
            model.device
        )

        # Step 4: Generate
        logger.info("Generating image description...")
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=128)

        # Step 5: Decode output
        text = processor.decode(outputs[0], skip_special_tokens=True)
        logger.info(f"Generated description: {text}")

        return text

    except Exception as e:
        logger.error(f"Error generating image description: {str(e)}")
        raise
