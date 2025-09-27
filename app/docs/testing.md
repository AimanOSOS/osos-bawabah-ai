# Testing Guide

This guide covers testing strategies and best practices for the Bawabah AI ML models API server.

## Table of Contents

- [Testing Strategy](#testing-strategy)
- [Test Setup](#test-setup)
- [Unit Testing](#unit-testing)
- [Integration Testing](#integration-testing)
- [API Testing](#api-testing)
- [Performance Testing](#performance-testing)
- [Test Data Management](#test-data-management)
- [Continuous Integration](#continuous-integration)

## Testing Strategy

### Testing Pyramid

```
    /\
   /  \     E2E Tests (Few)
  /____\    
 /      \   Integration Tests (Some)
/________\  
/          \ Unit Tests (Many)
/____________\
```

### Test Types

1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test service interactions
3. **API Tests**: Test HTTP endpoints
4. **Performance Tests**: Test response times and throughput
5. **End-to-End Tests**: Test complete user workflows

## Test Setup

### Dependencies

Add testing dependencies to `pyproject.toml`:

```toml
[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "^4.1.0"
httpx = "^0.24.0"
pytest-mock = "^3.11.0"
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Test configuration and fixtures
├── unit/                    # Unit tests
│   ├── test_services/
│   │   ├── test_tts_service.py
│   │   └── test_model_loader.py
│   └── test_config.py
├── integration/             # Integration tests
│   ├── test_api_integration.py
│   └── test_model_integration.py
├── api/                     # API tests
│   ├── test_tts_endpoints.py
│   └── test_health_endpoints.py
├── performance/             # Performance tests
│   └── test_performance.py
└── fixtures/                # Test data and fixtures
    ├── sample_audio.wav
    └── test_data.json
```

### Test Configuration

**conftest.py:**
```python
import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

@pytest.fixture
def temp_audio_file():
    """Create temporary audio file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        # Create a minimal WAV file
        f.write(b"RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x40\x1f\x00\x00\x80\x3e\x00\x00\x02\x00\x10\x00data\x00\x08\x00\x00")
        f.flush()
        yield f.name
    os.unlink(f.name)

@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    return {
        "tts_model_name": "test-model",
        "default_inference_timesteps": 5,
        "default_cfg_value": 1.0,
        "sample_rate": 16000,
        "max_text_length": 100
    }

@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Set up test environment."""
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
```

## Unit Testing

### Service Tests

**test_services/test_tts_service.py:**
```python
import pytest
from unittest.mock import Mock, patch
from app.services.tts_service import generate_simple_speech, generate_cloned_speech
from fastapi import UploadFile
import io

class TestTTSService:
    
    @patch('app.services.tts_service.get_tts_model')
    def test_generate_simple_speech_success(self, mock_get_model):
        """Test successful speech generation."""
        # Arrange
        mock_model = Mock()
        mock_model.generate.return_value = b"fake_audio_data"
        mock_get_model.return_value = mock_model
        
        # Act
        result = generate_simple_speech("Hello world")
        
        # Assert
        assert isinstance(result, bytes)
        assert len(result) > 0
        mock_model.generate.assert_called_once()
    
    @patch('app.services.tts_service.get_tts_model')
    def test_generate_simple_speech_short_text(self, mock_get_model):
        """Test speech generation with short text."""
        # Arrange
        mock_model = Mock()
        mock_model.generate.return_value = b"fake_audio_data"
        mock_get_model.return_value = mock_model
        
        # Act
        result = generate_simple_speech("Hi")
        
        # Assert
        assert isinstance(result, bytes)
        # Should add punctuation to short text
        mock_model.generate.assert_called_once()
    
    @patch('app.services.tts_service.get_tts_model')
    def test_generate_simple_speech_error(self, mock_get_model):
        """Test speech generation error handling."""
        # Arrange
        mock_model = Mock()
        mock_model.generate.side_effect = Exception("Model error")
        mock_get_model.return_value = mock_model
        
        # Act & Assert
        with pytest.raises(Exception, match="Model error"):
            generate_simple_speech("Hello world")
    
    @patch('app.services.tts_service.get_tts_model')
    @patch('tempfile.NamedTemporaryFile')
    def test_generate_cloned_speech_success(self, mock_temp_file, mock_get_model):
        """Test successful voice cloning."""
        # Arrange
        mock_model = Mock()
        mock_model.generate.return_value = b"fake_cloned_audio"
        mock_get_model.return_value = mock_model
        
        mock_file = Mock()
        mock_file.name = "/tmp/test.wav"
        mock_temp_file.return_value.__enter__.return_value = mock_file
        
        # Create mock upload file
        mock_upload = Mock(spec=UploadFile)
        mock_upload.file.read.return_value = b"fake_audio_data"
        
        # Act
        result = generate_cloned_speech("Hello", mock_upload, "Original text")
        
        # Assert
        assert isinstance(result, bytes)
        assert len(result) > 0
        mock_model.generate.assert_called_once()
```

### Model Loader Tests

**test_services/test_model_loader.py:**
```python
import pytest
from unittest.mock import patch, Mock
from app.services.model_loader import get_tts_model, _model_cache

class TestModelLoader:
    
    def setup_method(self):
        """Clear model cache before each test."""
        _model_cache.clear()
    
    @patch('app.services.model_loader.VoxCPM')
    def test_get_tts_model_first_load(self, mock_voxcpm):
        """Test model loading on first call."""
        # Arrange
        mock_model = Mock()
        mock_voxcpm.from_pretrained.return_value = mock_model
        
        # Act
        result = get_tts_model()
        
        # Assert
        assert result == mock_model
        mock_voxcpm.from_pretrained.assert_called_once_with("openbmb/VoxCPM-0.5B")
        assert "VoxCPM-0.5B" in _model_cache
    
    @patch('app.services.model_loader.VoxCPM')
    def test_get_tts_model_caching(self, mock_voxcpm):
        """Test model caching on subsequent calls."""
        # Arrange
        mock_model = Mock()
        mock_voxcpm.from_pretrained.return_value = mock_model
        
        # Act - call twice
        result1 = get_tts_model()
        result2 = get_tts_model()
        
        # Assert
        assert result1 == result2
        # Should only call from_pretrained once due to caching
        mock_voxcpm.from_pretrained.assert_called_once()
    
    @patch('app.services.model_loader.VoxCPM')
    def test_get_tts_model_error(self, mock_voxcpm):
        """Test model loading error handling."""
        # Arrange
        mock_voxcpm.from_pretrained.side_effect = Exception("Download failed")
        
        # Act & Assert
        with pytest.raises(Exception, match="Download failed"):
            get_tts_model()
```

### Configuration Tests

**test_config.py:**
```python
import pytest
from pydantic import ValidationError
from app.config import Settings

class TestSettings:
    
    def test_default_settings(self):
        """Test default configuration values."""
        settings = Settings()
        
        assert settings.tts_model_name == "openbmb/VoxCPM-0.5B"
        assert settings.default_inference_timesteps == 10
        assert settings.default_cfg_value == 2.0
        assert settings.sample_rate == 16000
        assert settings.debug is False
    
    def test_environment_override(self, monkeypatch):
        """Test environment variable override."""
        monkeypatch.setenv("TTS_MODEL_NAME", "custom-model")
        monkeypatch.setenv("DEBUG", "true")
        
        settings = Settings()
        
        assert settings.tts_model_name == "custom-model"
        assert settings.debug is True
    
    def test_validation_error(self, monkeypatch):
        """Test configuration validation."""
        monkeypatch.setenv("DEFAULT_INFERENCE_TIMESTEPS", "0")
        
        with pytest.raises(ValidationError):
            Settings()
    
    def test_log_level_validation(self, monkeypatch):
        """Test log level validation."""
        monkeypatch.setenv("LOG_LEVEL", "INVALID")
        
        with pytest.raises(ValidationError):
            Settings()
```

## Integration Testing

**test_integration/test_api_integration.py:**
```python
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

class TestAPIIntegration:
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @patch('app.services.tts_service.generate_simple_speech')
    def test_tts_end_to_end(self, mock_generate, client):
        """Test complete TTS workflow."""
        # Arrange
        mock_generate.return_value = b"fake_audio_data"
        
        # Act
        response = client.post(
            "/api/v1/text-to-speech/generate",
            json={"text": "Hello world"}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"
        assert response.headers["content-disposition"] == "attachment; filename=speech.wav"
        assert len(response.content) > 0
    
    @patch('app.services.tts_service.generate_cloned_speech')
    def test_voice_cloning_end_to_end(self, mock_generate, client, temp_audio_file):
        """Test complete voice cloning workflow."""
        # Arrange
        mock_generate.return_value = b"fake_cloned_audio"
        
        with open(temp_audio_file, "rb") as f:
            files = {"prompt_wav": ("test.wav", f, "audio/wav")}
            data = {
                "text": "Hello cloned voice",
                "prompt_text": "Original text"
            }
            
            # Act
            response = client.post(
                "/api/v1/text-to-speech/clone",
                files=files,
                data=data
            )
        
        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"
        assert response.headers["content-disposition"] == "attachment; filename=cloned_speech.wav"
```

## API Testing

**test_api/test_tts_endpoints.py:**
```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

class TestTTSEndpoints:
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to Bawabah AI"}
    
    @patch('app.services.tts_service.generate_simple_speech')
    def test_simple_tts_success(self, mock_generate, client):
        """Test successful simple TTS request."""
        # Arrange
        mock_generate.return_value = b"fake_audio_data"
        
        # Act
        response = client.post(
            "/api/v1/text-to-speech/generate",
            json={"text": "Hello world"}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"
        assert response.headers["content-disposition"] == "attachment; filename=speech.wav"
        assert response.headers["content-length"] == str(len(b"fake_audio_data"))
    
    def test_simple_tts_invalid_json(self, client):
        """Test TTS with invalid JSON."""
        response = client.post(
            "/api/v1/text-to-speech/generate",
            json={"invalid": "field"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_simple_tts_empty_text(self, client):
        """Test TTS with empty text."""
        response = client.post(
            "/api/v1/text-to-speech/generate",
            json={"text": ""}
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('app.services.tts_service.generate_simple_speech')
    def test_simple_tts_service_error(self, mock_generate, client):
        """Test TTS service error handling."""
        # Arrange
        mock_generate.side_effect = Exception("Service error")
        
        # Act
        response = client.post(
            "/api/v1/text-to-speech/generate",
            json={"text": "Hello world"}
        )
        
        # Assert
        assert response.status_code == 500
        assert "Service error" in response.json()["detail"]
    
    @patch('app.services.tts_service.generate_cloned_speech')
    def test_voice_cloning_success(self, mock_generate, client, temp_audio_file):
        """Test successful voice cloning."""
        # Arrange
        mock_generate.return_value = b"fake_cloned_audio"
        
        with open(temp_audio_file, "rb") as f:
            files = {"prompt_wav": ("test.wav", f, "audio/wav")}
            data = {
                "text": "Hello cloned voice",
                "prompt_text": "Original text"
            }
            
            # Act
            response = client.post(
                "/api/v1/text-to-speech/clone",
                files=files,
                data=data
            )
        
        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"
    
    def test_voice_cloning_missing_file(self, client):
        """Test voice cloning without audio file."""
        data = {
            "text": "Hello",
            "prompt_text": "Original"
        }
        
        response = client.post(
            "/api/v1/text-to-speech/clone",
            data=data
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_voice_cloning_invalid_file_type(self, client):
        """Test voice cloning with invalid file type."""
        files = {"prompt_wav": ("test.txt", b"not audio", "text/plain")}
        data = {
            "text": "Hello",
            "prompt_text": "Original"
        }
        
        response = client.post(
            "/api/v1/text-to-speech/clone",
            files=files,
            data=data
        )
        
        # Should still process but may fail in service layer
        assert response.status_code in [200, 500]
```

## Performance Testing

**test_performance/test_performance.py:**
```python
import pytest
import time
import concurrent.futures
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

class TestPerformance:
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @patch('app.services.tts_service.generate_simple_speech')
    def test_response_time(self, mock_generate, client):
        """Test API response time."""
        # Arrange
        mock_generate.return_value = b"fake_audio_data"
        
        # Act
        start_time = time.time()
        response = client.post(
            "/api/v1/text-to-speech/generate",
            json={"text": "Hello world"}
        )
        end_time = time.time()
        
        # Assert
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 1.0  # Should respond within 1 second
    
    @patch('app.services.tts_service.generate_simple_speech')
    def test_concurrent_requests(self, mock_generate, client):
        """Test handling of concurrent requests."""
        # Arrange
        mock_generate.return_value = b"fake_audio_data"
        
        def make_request():
            return client.post(
                "/api/v1/text-to-speech/generate",
                json={"text": "Hello world"}
            )
        
        # Act - make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [future.result() for future in futures]
        
        # Assert
        assert len(responses) == 10
        for response in responses:
            assert response.status_code == 200
    
    @patch('app.services.tts_service.generate_simple_speech')
    def test_memory_usage(self, mock_generate, client):
        """Test memory usage with large responses."""
        # Arrange
        large_audio = b"fake_audio_data" * 1000  # Simulate large audio
        mock_generate.return_value = large_audio
        
        # Act
        response = client.post(
            "/api/v1/text-to-speech/generate",
            json={"text": "Hello world"}
        )
        
        # Assert
        assert response.status_code == 200
        assert len(response.content) == len(large_audio)
```

## Test Data Management

### Test Fixtures

**fixtures/test_data.json:**
```json
{
  "sample_texts": [
    "Hello world",
    "This is a test",
    "Short",
    "A very long text that exceeds the normal length and tests the system's ability to handle longer inputs properly"
  ],
  "invalid_inputs": [
    "",
    null,
    "x".repeat(10001)
  ],
  "expected_responses": {
    "simple_tts": {
      "content_type": "audio/wav",
      "disposition": "attachment; filename=speech.wav"
    }
  }
}
```

### Test Audio Files

Create minimal test audio files:

```python
# create_test_audio.py
import wave
import struct

def create_test_wav(filename, duration=1.0, sample_rate=16000):
    """Create a minimal test WAV file."""
    num_samples = int(sample_rate * duration)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Generate simple sine wave
        for i in range(num_samples):
            value = int(32767 * 0.1 * (i / num_samples))
            wav_file.writeframes(struct.pack('<h', value))

# Create test files
create_test_wav("tests/fixtures/sample_audio.wav", 2.0)
```

## Continuous Integration

### GitHub Actions

**.github/workflows/test.yml:**
```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.13]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install Poetry
      uses: snok/install-poetry@v1
      with:
        version: latest
        virtualenvs-create: true
        virtualenvs-in-project: true
    
    - name: Load cached venv
      id: cached-poetry-dependencies
      uses: actions/cache@v3
      with:
        path: .venv
        key: venv-${{ runner.os }}-${{ matrix.python-version }}-${{ hashFiles('**/poetry.lock') }}
    
    - name: Install dependencies
      if: steps.cached-poetry-dependencies.outputs.cache-hit != 'true'
      run: poetry install --no-interaction --no-root
    
    - name: Install project
      run: poetry install --no-interaction
    
    - name: Run tests
      run: poetry run pytest --cov=app --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
```

### Test Commands

**Makefile:**
```makefile
.PHONY: test test-unit test-integration test-api test-coverage

test:
	poetry run pytest

test-unit:
	poetry run pytest tests/unit/

test-integration:
	poetry run pytest tests/integration/

test-api:
	poetry run pytest tests/api/

test-coverage:
	poetry run pytest --cov=app --cov-report=html --cov-report=term

test-performance:
	poetry run pytest tests/performance/ -v

lint:
	poetry run flake8 app/
	poetry run black --check app/
	poetry run isort --check-only app/

format:
	poetry run black app/
	poetry run isort app/
```

## Running Tests

### Local Testing

```bash
# Run all tests
poetry run pytest

# Run specific test categories
poetry run pytest tests/unit/
poetry run pytest tests/integration/
poetry run pytest tests/api/

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/unit/test_tts_service.py

# Run specific test function
poetry run pytest tests/unit/test_tts_service.py::TestTTSService::test_generate_simple_speech_success

# Run with verbose output
poetry run pytest -v

# Run tests in parallel
poetry run pytest -n auto
```

### Test Environment

```bash
# Set test environment variables
export DEBUG=true
export LOG_LEVEL=DEBUG
export TTS_MODEL_NAME=test-model

# Run tests
poetry run pytest
```

This comprehensive testing guide provides strategies and examples for testing the Bawabah AI API server at all levels, from unit tests to performance testing.
