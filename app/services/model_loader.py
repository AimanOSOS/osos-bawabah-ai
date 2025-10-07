from voxcpm import VoxCPM

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
