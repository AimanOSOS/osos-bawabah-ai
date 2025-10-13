# Bawabah AI - ML Models API Server

A scalable FastAPI-based server for accessing machine learning models through REST API calls. This application provides easy-to-use endpoints for various ML models, starting with Text-to-Speech (TTS) capabilities.

## Features

- ⚡ **FastAPI Framework**: High-performance async API with automatic OpenAPI documentation
- 🔧 **Configurable**: Environment-based configuration for easy deployment
- 📦 **Model Caching**: Efficient model loading and caching for better performance
- 🛡️ **Error Handling**: Comprehensive error handling and logging
- 🐳 **Docker Support**: Easy deployment with Docker and Docker Compose

## Quick Start

### Prerequisites

- Python 3.12+ (for local development)
- Poetry (for dependency management)
- Docker and Docker Compose (for containerized deployment)

   **Clone the repository**
   ```bash
   git clone https://github.com/AimanOSOS/osos-bawabah-ai.git
   cd osos-bawabah-ai
   ```

  **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env file with your preferred settings
   ```

### Option 1: Docker Deployment (Recommended)


1. **Build and run with Docker Compose**
   ```bash
   # First time build (will be slow minutes due to ML dependencies)
   docker-compose up --build
   
   # Subsequent builds (much faster minutes due to layer caching)
   docker-compose up --build
   
   # Code-only changes (very fast - 10-30 seconds)
   docker-compose up --build
   ```

   Or run in detached mode:
   ```bash
   docker-compose up --build -d
   ```

2. **Access the application**
   The API will be available at `http://localhost:6060`

### Option 2: Local Development


1. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env file with your preferred settings
   ```

2. **Run the application**
   ```bash
   poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 6060
   ```

   The API will be available at `http://localhost:6060`

### Docker Build Options

#### Standard Build
```bash
docker build -f app/Dockerfile -t bawabah-ai .
```

#### CUDA-enabled Build (for GPU acceleration)
```bash
docker build -f app/Dockerfile --build-arg USE_CUDA=true -t bawabah-ai:cuda .
```

#### Optimized Build Commands

**First time build (will be slow)**
```bash
docker-compose build
```

**Subsequent builds (much faster due to layer caching)**
```bash
docker-compose build
```

**For development with persistent cache**
```bash
# Build with cache volume for Hugging Face models
docker-compose up --build

# The cache volume will persist between builds, making subsequent builds even faster
```

#### Build Performance Tips

- **Layer Caching**: Dependencies are cached in separate layers, so only code changes trigger fast rebuilds
- **Cache Volume**: Hugging Face model cache persists between builds via Docker volume
- **Dependency Changes**: Only rebuilds dependency layer when `pyproject.toml` or `poetry.lock` changes
- **Code Changes**: Only rebuilds final layer when source code changes

#### Run Docker Container
```bash
# Standard container
docker run -p 6060:6060 bawabah-ai

# CUDA-enabled container (requires nvidia-docker)
docker run --gpus all -p 6060:6060 bawabah-ai:cuda
```

### API Documentation

Once the server is running, you can access:
- **Interactive API docs**: `http://localhost:6060/docs`
- **ReDoc documentation**: `http://localhost:6060/redoc`
- **OpenAPI schema**: `http://localhost:6060/openapi.json`

## API Endpoints

### Health Check
- `GET /` - Welcome message and health check

### Text-to-Speech
- `POST /api/v1/text-to-speech/generate` - Generate speech from text
- `POST /api/v1/text-to-speech/clone` - Clone voice and generate speech

## Example Usage

### Simple Text-to-Speech

```bash
curl -X POST "http://localhost:6060/api/v1/text-to-speech/generate" \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello, this is a test of the text to speech system."}'
```

### Voice Cloning

```bash
curl -X POST "http://localhost:6060/api/v1/text-to-speech/clone" \
     -F "text=Hello, this is my cloned voice." \
     -F "prompt_wav=@voice_sample.wav" \
     -F "prompt_text=This is the original text from the voice sample."
```

## Configuration

The application uses environment variables for configuration. See `env.example` for all available options:

- `TTS_MODEL_NAME`: Model to use for TTS (default: "openbmb/VoxCPM-0.5B")
- `DEFAULT_INFERENCE_TIMESTEPS`: Number of inference steps (default: 10)
- `DEFAULT_CFG_VALUE`: Classifier-free guidance value (default: 2.0)
- `SAMPLE_RATE`: Audio sample rate (default: 16000)
- `DEBUG`: Enable debug mode (default: false)

## Development

For detailed development information, including how to add new ML models, see the [Development Guide](docs/development.md).

## Project Structure

```
osos-bawabah-ai/
├── app/                    # Main application code
│   ├── main.py            # FastAPI appl
│   ├── config.py          # Configuration management
│   ├── routers/           # API route handlers
│   │   └── tts.py        # Text-to-speech endpoints
│   └── services/          # Business logic services
│       ├── tts_service.py # TTS service implementation
│       └── model_loader.py # Model loading and caching
├── docs/                  # Detailed documentation
├── tests/                 # Test files
├── pyproject.toml         # Project dependencies and metadata
└── env.example           # Environment variables template
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request to dev branch

## License

[Add your license information here]

## Support


For questions and support, please contact: aiman.madan@osos.om


