# Development Guide

This guide explains how to develop and extend the Bawabah AI ML models API server.

## Table of Contents

- [Project Structure](#project-structure)
- [Adding New ML Models](#adding-new-ml-models)
- [Creating New API Endpoints](#creating-new-api-endpoints)
- [Configuration Management](#configuration-management)
- [Model Loading and Caching](#model-loading-and-caching)
- [Error Handling](#error-handling)
- [Testing](#testing)
- [Code Style and Standards](#code-style-and-standards)

## Project Structure

```
app/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration management with Pydantic
├── routers/             # API route handlers
│   ├── __init__.py
│   └── tts.py          # Text-to-speech endpoints
└── services/            # Business logic services
    ├── __init__.py
    ├── model_loader.py  # Model loading and caching
    └── tts_service.py   # TTS service implementation
```

### Key Components

- **Routers**: Handle HTTP requests and responses, input validation
- **Services**: Contain business logic and model interactions
- **Config**: Centralized configuration management
- **Model Loader**: Handles model loading, caching, and lifecycle

## Adding New ML Models

### Step 1: Create a New Service

Create a new service file in `app/services/` for your model:

```python
# app/services/image_classification_service.py
import logging
from .model_loader import get_image_classification_model
from ..config import settings

logger = logging.getLogger(__name__)

def classify_image(image_data: bytes) -> dict:
    """Classify an image and return predictions."""
    model = get_image_classification_model()
    
    try:
        # Your model inference logic here
        predictions = model.predict(image_data)
        
        return {
            "predictions": predictions,
            "model_version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Image classification failed: {str(e)}")
        raise
```

### Step 2: Add Model Loading

Update `app/services/model_loader.py`:

```python
# Add to model_loader.py
from transformers import AutoModel, AutoTokenizer

def get_image_classification_model():
    """Loads and caches the image classification model."""
    model_name = "ImageClassificationModel"
    if model_name not in _model_cache:
        print("Loading image classification model...")
        _model_cache[model_name] = AutoModel.from_pretrained("your-model-name")
        print("Image classification model loaded.")
    return _model_cache[model_name]
```

### Step 3: Create API Router

Create a new router in `app/routers/`:

```python
# app/routers/image_classification.py
from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
import logging
from ..services import image_classification_service

router = APIRouter()
logger = logging.getLogger(__name__)

class ClassificationResponse(BaseModel):
    predictions: list
    model_version: str

@router.post("/image-classification/classify", 
             response_model=ClassificationResponse,
             tags=["Image Classification"])
async def classify_image(image: UploadFile = File(...)):
    """
    Classify an uploaded image.
    """
    try:
        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image data
        image_data = await image.read()
        
        # Classify image
        result = image_classification_service.classify_image(image_data)
        
        return ClassificationResponse(**result)
        
    except Exception as e:
        logger.error(f"Image classification failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 4: Register Router

Update `app/main.py`:

```python
from fastapi import FastAPI
from .routers import tts, image_classification  # Add new import

app = FastAPI(
    title="Bawabah AI",
    description="An API server for various machine learning models.",
    version="1.0.0",
)

# Include routers
app.include_router(tts.router, prefix="/api/v1")
app.include_router(image_classification.router, prefix="/api/v1")  # Add new router
```

### Step 5: Add Configuration

Update `app/config.py` to add model-specific settings:

```python
class Settings(BaseSettings):
    # Existing settings...
    
    # Image Classification Settings
    image_classification_model_name: str = Field(
        default="your-model-name",
        description="Image classification model name"
    )
    max_image_size: int = Field(
        default=1024,
        description="Maximum image size in pixels"
    )
    allowed_image_formats: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".bmp"],
        description="Allowed image file formats"
    )
```

## Creating New API Endpoints

### Request/Response Models

Use Pydantic models for request/response validation:

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional

class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000, description="Text to analyze")
    language: Optional[str] = Field(default="en", description="Text language code")
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty')
        return v.strip()

class TextAnalysisResponse(BaseModel):
    sentiment: str = Field(..., description="Sentiment classification")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    entities: List[str] = Field(default=[], description="Named entities found")
```

### Error Handling

Implement consistent error handling:

```python
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

@router.post("/analyze-text")
async def analyze_text(request: TextAnalysisRequest):
    try:
        # Your logic here
        result = analyze_service.process_text(request.text, request.language)
        return result
        
    except ValueError as e:
        logger.warning(f"Invalid input: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Text analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

## Configuration Management

### Environment Variables

Add new configuration options to `app/config.py`:

```python
class Settings(BaseSettings):
    # Add new fields with proper validation
    new_model_name: str = Field(
        default="default-model",
        description="Description of the new setting"
    )
    
    # Add validation if needed
    @validator('new_model_name')
    def validate_model_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Model name cannot be empty')
        return v.strip()
    
    class Config:
        # Add environment variable mapping
        fields = {
            "new_model_name": {"env": "NEW_MODEL_NAME"},
        }
```

### Using Configuration

Access configuration in your services:

```python
from ..config import settings

def my_service_function():
    model_name = settings.new_model_name
    # Use the configuration value
```

## Model Loading and Caching

### Model Cache Pattern

Follow the established pattern in `model_loader.py`:

```python
# Global model cache
_model_cache = {}

def get_my_model():
    """Loads and caches a model."""
    model_name = "MyModel"
    if model_name not in _model_cache:
        print(f"Loading {model_name}...")
        _model_cache[model_name] = load_model_function()
        print(f"{model_name} loaded.")
    return _model_cache[model_name]
```

### Model Lifecycle Management

For models that need cleanup:

```python
import atexit

def cleanup_models():
    """Cleanup function for model resources."""
    for model_name, model in _model_cache.items():
        if hasattr(model, 'cleanup'):
            model.cleanup()

# Register cleanup function
atexit.register(cleanup_models)
```

## Error Handling

### Logging

Use structured logging throughout the application:

```python
import logging

logger = logging.getLogger(__name__)

def my_function():
    logger.info("Starting operation")
    try:
        # Your code here
        logger.info("Operation completed successfully")
    except Exception as e:
        logger.error(f"Operation failed: {str(e)}", exc_info=True)
        raise
```

### Custom Exceptions

Create custom exceptions for better error handling:

```python
# app/exceptions.py
class ModelLoadError(Exception):
    """Raised when model loading fails."""
    pass

class InferenceError(Exception):
    """Raised when model inference fails."""
    pass
```

## Testing

### Unit Tests

Create tests in the `tests/` directory:

```python
# tests/test_image_classification.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_classify_image():
    # Test with a sample image
    with open("tests/sample_image.jpg", "rb") as f:
        response = client.post(
            "/api/v1/image-classification/classify",
            files={"image": f}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert "model_version" in data
```

### Integration Tests

Test the full pipeline:

```python
def test_full_pipeline():
    # Test the complete flow from request to response
    pass
```

## Code Style and Standards

### Python Style

- Follow PEP 8
- Use type hints for all function parameters and return values
- Use docstrings for all public functions and classes
- Keep functions small and focused

### FastAPI Best Practices

- Use Pydantic models for request/response validation
- Implement proper HTTP status codes
- Use dependency injection for shared resources
- Add comprehensive OpenAPI documentation

### Example Function

```python
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def process_data(
    input_data: List[str], 
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Process input data according to configuration.
    
    Args:
        input_data: List of strings to process
        config: Configuration dictionary
        
    Returns:
        Dictionary containing processed results
        
    Raises:
        ValueError: If input_data is empty
        RuntimeError: If processing fails
    """
    if not input_data:
        raise ValueError("Input data cannot be empty")
    
    logger.info(f"Processing {len(input_data)} items")
    
    try:
        # Processing logic here
        result = {"processed": input_data, "config": config}
        logger.info("Processing completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise RuntimeError(f"Failed to process data: {str(e)}")
```

## Next Steps

1. **Add Monitoring**: Implement metrics and health checks
2. **Add Authentication**: Implement API key or OAuth authentication
3. **Add Rate Limiting**: Implement request rate limiting
4. **Add Caching**: Implement response caching for expensive operations
5. **Add Batch Processing**: Support batch requests for better efficiency

For more information, see the [API Reference](api.md) and [Architecture](architecture.md) documentation.
