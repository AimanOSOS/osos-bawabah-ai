from voxcpm import VoxCPM
from transformers import AutoProcessor, AutoModelForVision2Seq
import torch
import os

# A simple cache to store the loaded models
_model_cache = {}


def get_tts_model() -> VoxCPM:
    """Loads and caches the VoxCPM TTS model."""
    model_name = "VoxCPM-0.5B"
    if model_name not in _model_cache:
        print("Loading TTS model...")
        _model_cache[model_name] = VoxCPM.from_pretrained("openbmb/VoxCPM-0.5B")
        print("TTS model Loaded.")
    return _model_cache[model_name]


def get_granite_vision_model():
    """Loads and caches the IBM Granite Vision 3.2-2B model."""
    model_name = "ibm-granite/granite-vision-3.2-2b"
    if model_name not in _model_cache:
        print("🔄 Loading IBM Granite Vision 3.2-2B...")

        cache_dir = os.getenv("MODEL_CACHE_DIR", None)
        processor = AutoProcessor.from_pretrained(
            model_name, cache_dir=cache_dir, trust_remote_code=True
        )
        model = AutoModelForVision2Seq.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            cache_dir=cache_dir,
            trust_remote_code=True,
        )

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)

        _model_cache[model_name] = (model, processor)
        print("✅ IBM Granite Vision 3.2-2B loaded successfully.")

    return _model_cache[model_name]
