# API Reference

Complete documentation for the Bawabah AI ML models API endpoints.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. Future versions may include API key authentication.

## Content Types

- **JSON**: `application/json` for structured data
- **Multipart**: `multipart/form-data` for file uploads
- **Audio**: `audio/wav` for audio responses

## Error Responses

All endpoints return consistent error responses:

```json
{
  "detail": "Error message description"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `422`: Validation Error (invalid request format)
- `500`: Internal Server Error

## Endpoints

### Health Check

#### GET /

Check API health and get welcome message.

**Response:**
```json
{
  "message": "Welcome to Bawabah AI"
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/"
```

---

## Text-to-Speech Endpoints

### POST /api/v1/text-to-speech/generate

Generate speech from text using default voice settings.

**Request Body:**
```json
{
  "text": "Hello, this is a test of the text to speech system."
}
```

**Parameters:**
- `text` (string, required): Text to convert to speech (max 1000 characters)

**Response:**
- **Content-Type**: `audio/wav`
- **Content-Disposition**: `attachment; filename=speech.wav`
- **Body**: WAV audio file bytes

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/text-to-speech/generate" \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello, this is a test of the text to speech system."}' \
     --output speech.wav
```

**Error Responses:**
- `400`: Invalid text input
- `500`: TTS generation failed

---

### POST /api/v1/text-to-speech/clone

Generate speech by cloning a voice from an uploaded audio sample.

**Request Body:** `multipart/form-data`

**Parameters:**
- `text` (string, required): Text to synthesize in the cloned voice
- `prompt_wav` (file, required): Audio file (.wav) containing the voice to clone
- `prompt_text` (string, required): Exact transcription of the prompt audio

**Response:**
- **Content-Type**: `audio/wav`
- **Content-Disposition**: `attachment; filename=cloned_speech.wav`
- **Body**: WAV audio file bytes

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/text-to-speech/clone" \
     -F "text=Hello, this is my cloned voice speaking." \
     -F "prompt_wav=@voice_sample.wav" \
     -F "prompt_text=This is the original text from the voice sample." \
     --output cloned_speech.wav
```

**Error Responses:**
- `400`: Invalid file format or missing parameters
- `500`: Voice cloning failed

**File Requirements:**
- **Format**: WAV audio file
- **Sample Rate**: 16kHz (recommended)
- **Duration**: 3-10 seconds (optimal for voice cloning)
- **Quality**: Clear speech without background noise

---

## Speech-to-Text Endpoints

### POST /api/v1/speech-to-text/generate

Convert speech to text using Whisper Large model with detailed output.

**Request Body:** `multipart/form-data`

**Parameters:**
- `audio_file` (file, required): Audio file for transcription
  - **Supported formats**: MP3, WAV, WebM
  - **Content types**: 
    - `audio/mpeg`, `audio/mp3` (MP3)
    - `audio/wav`, `audio/wave`, `audio/x-wav` (WAV)
    - `audio/webm` (WebM)

**Response:**
- **Content-Type**: `application/json`
- **Body**: Comprehensive transcription data with word-level timestamps

**Example Response:**
```json
{
  "detected_language": "en",
  "full_text": "Hello, this is a test of the speech to text system.",
  "total_duration": 5.2,
  "segments": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": "Hello, this is a test",
      "confidence": -0.8,
      "words": [
        {
          "word": "Hello,",
          "start": 0.0,
          "end": 0.5,
          "confidence": 0.95
        }
      ]
    }
  ],
  "metadata": {
    "model": "whisper-large",
    "sample_rate": 16000,
    "chunks_processed": 1,
    "original_segments": 2,
    "merged_segments": 2
  }
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/speech-to-text/generate" \
     -F "audio_file=@sample_audio.wav" \
     -H "Accept: application/json"
```

**Error Responses:**
- `400`: Invalid file format or unsupported audio type
- `500`: Transcription failed

**File Requirements:**
- **Formats**: MP3, WAV, WebM
- **Sample Rate**: Any (automatically converted to 16kHz)
- **Duration**: No limit (automatically chunked for long files)
- **Quality**: Higher quality audio produces better results

---

## Configuration Parameters

The following parameters can be configured via environment variables:

### Model Configuration
- `TTS_MODEL_NAME`: TTS model name (default: "openbmb/VoxCPM-0.5B")
- `WHISPER_MODEL_NAME`: STT model name (default: "whisper-large")
- `MODEL_CACHE_DIR`: Directory for model caching

### TTS Parameters
- `DEFAULT_INFERENCE_TIMESTEPS`: Number of inference steps (default: 10)
- `DEFAULT_CFG_VALUE`: Classifier-free guidance value (default: 2.0)
- `DEFAULT_RETRY_MAX_TIMS`: Maximum retry attempts (default: 3)
- `DEFAULT_RETRY_RATIO_THRESHOLD`: Retry threshold ratio (default: 6.0)

### Audio Settings
- `SAMPLE_RATE`: Audio sample rate in Hz (default: 16000)
- `AUDIO_FORMAT`: Default audio format (default: "WAV")

### STT Parameters
- `STT_CHUNK_SIZE`: Audio chunk size in seconds (default: 30)
- `STT_OVERLAP_SIZE`: Overlap between chunks in seconds (default: 2)
- `STT_OVERLAP_THRESHOLD`: Word overlap detection threshold (default: 1.5)
- `STT_GAP_THRESHOLD`: Segment gap threshold for merging (default: 2.0)

### API Settings
- `MAX_TEXT_LENGTH`: Maximum text length for processing (default: 1000)
- `ALLOWED_AUDIO_FORMATS`: Allowed audio file formats (default: [".wav", ".mp3", ".flac"])

### Application Settings
- `DEBUG`: Enable debug mode (default: false)
- `LOG_LEVEL`: Logging level (default: "INFO")

## Rate Limiting

Currently, no rate limiting is implemented. Future versions may include:
- Requests per minute limits
- Concurrent request limits
- Resource usage limits

## Caching

- **Models**: Automatically cached in memory after first load
- **Responses**: No response caching currently implemented
- **Files**: Temporary files are cleaned up after processing

## WebSocket Support

WebSocket endpoints are not currently available. Future versions may include:
- Real-time audio streaming
- Live voice cloning
- Interactive TTS sessions

## SDK Examples

### Python

```python
import requests
import json

# Simple TTS
def generate_speech(text):
    url = "http://localhost:8000/api/v1/text-to-speech/generate"
    data = {"text": text}
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        with open("speech.wav", "wb") as f:
            f.write(response.content)
        return "speech.wav"
    else:
        raise Exception(f"TTS failed: {response.text}")

# Voice cloning
def clone_voice(text, prompt_audio_path, prompt_text):
    url = "http://localhost:8000/api/v1/text-to-speech/clone"
    
    with open(prompt_audio_path, "rb") as f:
        files = {"prompt_wav": f}
        data = {
            "text": text,
            "prompt_text": prompt_text
        }
        
        response = requests.post(url, files=files, data=data)
    
    if response.status_code == 200:
        with open("cloned_speech.wav", "wb") as f:
            f.write(response.content)
        return "cloned_speech.wav"
    else:
        raise Exception(f"Voice cloning failed: {response.text}")

# STT transcription
def transcribe_audio(audio_file_path):
    url = "http://localhost:8000/api/v1/speech-to-text/generate"
    
    with open(audio_file_path, "rb") as f:
        files = {"audio_file": f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Transcription failed: {response.text}")

# Usage
generate_speech("Hello, world!")
clone_voice("Hello, this is my voice", "sample.wav", "This is a sample")
result = transcribe_audio("audio.wav")
print(f"Transcribed: {result['full_text']}")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');
const fs = require('fs');

// Simple TTS
async function generateSpeech(text) {
    try {
        const response = await axios.post(
            'http://localhost:8000/api/v1/text-to-speech/generate',
            { text: text },
            { responseType: 'arraybuffer' }
        );
        
        fs.writeFileSync('speech.wav', response.data);
        return 'speech.wav';
    } catch (error) {
        throw new Error(`TTS failed: ${error.response?.data?.detail || error.message}`);
    }
}

// Voice cloning
async function cloneVoice(text, promptAudioPath, promptText) {
    try {
        const formData = new FormData();
        formData.append('text', text);
        formData.append('prompt_wav', fs.createReadStream(promptAudioPath));
        formData.append('prompt_text', promptText);
        
        const response = await axios.post(
            'http://localhost:8000/api/v1/text-to-speech/clone',
            formData,
            { 
                responseType: 'arraybuffer',
                headers: { 'Content-Type': 'multipart/form-data' }
            }
        );
        
        fs.writeFileSync('cloned_speech.wav', response.data);
        return 'cloned_speech.wav';
    } catch (error) {
        throw new Error(`Voice cloning failed: ${error.response?.data?.detail || error.message}`);
    }
}

// STT transcription
async function transcribeAudio(audioFilePath) {
    try {
        const formData = new FormData();
        const file = fs.readFileSync(audioFilePath);
        const blob = new Blob([file]);
        formData.append('audio_file', blob, 'audio.wav');
        
        const response = await axios.post(
            'http://localhost:8000/api/v1/speech-to-text/generate',
            formData,
            { headers: { 'Content-Type': 'multipart/form-data' } }
        );
        
        return response.data;
    } catch (error) {
        throw new Error(`Transcription failed: ${error.response?.data?.detail || error.message}`);
    }
}

// Usage
generateSpeech("Hello, world!")
    .then(filename => console.log(`Generated: ${filename}`))
    .catch(error => console.error(error));

transcribeAudio("audio.wav")
    .then(result => console.log(`Transcribed: ${result.full_text}`))
    .catch(error => console.error(error));
```

### cURL Examples

```bash
# Health check
curl -X GET "http://localhost:8000/"

# Simple TTS
curl -X POST "http://localhost:8000/api/v1/text-to-speech/generate" \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello, this is a test."}' \
     --output speech.wav

# Voice cloning
curl -X POST "http://localhost:8000/api/v1/text-to-speech/clone" \
     -F "text=Hello, this is my cloned voice." \
     -F "prompt_wav=@voice_sample.wav" \
     -F "prompt_text=This is the original text." \
     --output cloned_speech.wav

# Speech-to-text transcription
curl -X POST "http://localhost:8000/api/v1/speech-to-text/generate" \
     -F "audio_file=@sample_audio.wav" \
     -H "Accept: application/json"
```

## OpenAPI Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## Versioning

The API uses URL versioning:
- Current version: `v1`
- Base path: `/api/v1/`

Future versions will be available at `/api/v2/`, etc.

## Changelog

### v1.0.0
- Initial release
- Text-to-speech generation
- Voice cloning functionality
- Speech-to-text transcription with Whisper Large model
- Word-level timestamps and confidence scores
- Automatic language detection
- Chunked audio processing for long files
- Basic error handling and logging
