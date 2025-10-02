# Bawabah AI - ML Models API Server

A scalable FastAPI-based server for accessing machine learning models through REST API calls. This application provides easy-to-use endpoints for various ML models, starting with Text-to-Speech (TTS) capabilities.

## Features

- 🎤 **Text-to-Speech Generation**: Convert text to speech with high-quality audio output
- 🎭 **Voice Cloning**: Clone voices from audio samples for personalized speech synthesis
- ⚡ **FastAPI Framework**: High-performance async API with automatic OpenAPI documentation
- 🔧 **Configurable**: Environment-based configuration for easy deployment
- 📦 **Model Caching**: Efficient model loading and caching for better performance
- 🛡️ **Error Handling**: Comprehensive error handling and logging

## Quick Start

### Prerequisites

- Python 3.13+
- Poetry (for dependency management)

### Installation

1. **Clone the repository**
   ```bash
   git clone [<repository-url>](https://github.com/AimanOSOS/osos-bawabah-ai.git)
   cd osos-bawabah-ai
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env file with your preferred settings
   ```

4. **Run the application**
   ```bash
   poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 9696
   ```

The API will be available at `http://localhost:9696`

### API Documentation

Once the server is running, you can access:
- **Interactive API docs**: `http://localhost:9696/docs`
- **ReDoc documentation**: `http://localhost:9696/redoc`
- **OpenAPI schema**: `http://localhost:9696/openapi.json`

## API Endpoints

### Health Check
- `GET /` - Welcome message and health check

### Text-to-Speech
- `POST /api/v1/text-to-speech/generate` - Generate speech from text
- `POST /api/v1/text-to-speech/clone` - Clone voice and generate speech

## Example Usage

### Simple Text-to-Speech

```bash
curl -X POST "http://localhost:9696/api/v1/text-to-speech/generate" \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello, this is a test of the text to speech system."}'
```

### Voice Cloning

```bash
curl -X POST "http://localhost:9696/api/v1/text-to-speech/clone" \
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
│   ├── main.py            # FastAPI application entry point
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
5. Submit a pull request

## License

[Add your license information here]

## Support


For questions and support, please contact: aiman.madan@osos.om
