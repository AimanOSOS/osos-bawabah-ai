# Speech-to-Text (STT) Module Documentation

This document provides comprehensive documentation for the Speech-to-Text (STT) module in the Bawabah AI API server.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [API Endpoints](#api-endpoints)
- [Service Functions](#service-functions)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Error Handling](#error-handling)
- [Performance Considerations](#performance-considerations)
- [Troubleshooting](#troubleshooting)

## Overview

The STT module provides speech-to-text transcription capabilities using the Whisper Large model. It supports multiple audio formats and provides detailed transcription output with word-level timestamps, confidence scores, and language detection.

### Key Features

- **Multi-format Support**: MP3, WAV, and WebM audio formats
- **High Accuracy**: Uses Whisper Large model for superior transcription quality
- **Detailed Output**: Word-level timestamps and confidence scores
- **Language Detection**: Automatic language detection
- **Chunked Processing**: Handles long audio files by processing in chunks
- **Overlap Removal**: Intelligent removal of duplicate words from chunk overlaps
- **Comprehensive Metadata**: Detailed information about the transcription process

## Architecture

### Component Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   STT Router    │    │  STT Service    │    │  Model Loader   │
│   (stt.py)      │    │(stt_service.py) │    │(model_loader.py)│
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │ 1. File Upload       │                      │
          ├─────────────────────►│                      │
          │                      │ 2. Audio Processing  │
          │                      ├─────────────────────►│
          │                      │                      │
          │ 3. Transcription     │ 3. Whisper Model     │
          │◄─────────────────────┤◄─────────────────────┤
          │                      │                      │
          │ 4. JSON Response     │                      │
          │◄─────────────────────┤                      │
```

### Data Flow

1. **File Upload**: Client uploads audio file via multipart form data
2. **Validation**: Router validates file type and content
3. **Temporary Storage**: File saved to temporary location with proper extension
4. **Audio Processing**: Service loads and preprocesses audio
5. **Chunking**: Long audio files split into 30-second chunks with 2-second overlap
6. **Transcription**: Each chunk processed by Whisper model
7. **Segmentation**: Results combined and overlapping words removed
8. **Response**: Comprehensive JSON response with transcription data
9. **Cleanup**: Temporary files removed

## API Endpoints

### POST /api/v1/speech-to-text/generate

Converts speech to text using Whisper Large model with detailed output.

#### Request

**Content-Type**: `multipart/form-data`

**Parameters**:
- `audio_file` (file, required): Audio file for transcription
  - **Supported formats**: MP3, WAV, WebM
  - **Content types**: 
    - `audio/mpeg`, `audio/mp3` (MP3)
    - `audio/wav`, `audio/wave`, `audio/x-wav` (WAV)
    - `audio/webm` (WebM)

#### Response

**Content-Type**: `application/json`

**Success Response (200)**:
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
        },
        {
          "word": "this",
          "start": 0.6,
          "end": 0.8,
          "confidence": 0.92
        },
        {
          "word": "is",
          "start": 0.9,
          "end": 1.0,
          "confidence": 0.98
        },
        {
          "word": "a",
          "start": 1.1,
          "end": 1.2,
          "confidence": 0.99
        },
        {
          "word": "test",
          "start": 1.3,
          "end": 1.8,
          "confidence": 0.94
        }
      ]
    },
    {
      "start": 2.6,
      "end": 5.2,
      "text": "of the speech to text system.",
      "confidence": -0.7,
      "words": [
        {
          "word": "of",
          "start": 2.6,
          "end": 2.8,
          "confidence": 0.97
        },
        {
          "word": "the",
          "start": 2.9,
          "end": 3.0,
          "confidence": 0.99
        },
        {
          "word": "speech",
          "start": 3.1,
          "end": 3.6,
          "confidence": 0.93
        },
        {
          "word": "to",
          "start": 3.7,
          "end": 3.8,
          "confidence": 0.98
        },
        {
          "word": "text",
          "start": 3.9,
          "end": 4.2,
          "confidence": 0.96
        },
        {
          "word": "system.",
          "start": 4.3,
          "end": 5.2,
          "confidence": 0.91
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

#### Error Responses

**400 Bad Request**:
```json
{
  "detail": "File must be an audio file in MP3, WAV, or WebM format"
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Transcription failed: [error message]"
}
```

#### Example Usage

**cURL**:
```bash
curl -X POST "http://localhost:8000/api/v1/speech-to-text/generate" \
     -F "audio_file=@sample_audio.wav" \
     -H "Accept: application/json"
```

**Python**:
```python
import requests

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
result = transcribe_audio("sample_audio.wav")
print(f"Transcribed text: {result['full_text']}")
print(f"Detected language: {result['detected_language']}")
```

**JavaScript**:
```javascript
async function transcribeAudio(audioFile) {
    const formData = new FormData();
    formData.append('audio_file', audioFile);
    
    try {
        const response = await fetch('/api/v1/speech-to-text/generate', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            return await response.json();
        } else {
            throw new Error(`Transcription failed: ${response.statusText}`);
        }
    } catch (error) {
        console.error('Transcription error:', error);
        throw error;
    }
}

// Usage
const fileInput = document.getElementById('audioFile');
fileInput.addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (file) {
        try {
            const result = await transcribeAudio(file);
            console.log('Transcribed text:', result.full_text);
            console.log('Detected language:', result.detected_language);
        } catch (error) {
            console.error('Error:', error);
        }
    }
});
```

## Service Functions

### Core Functions

#### `transcribe_audio(audio_file_path: str) -> Dict[str, Any]`

Main transcription function that processes audio files and returns comprehensive transcription data.

**Parameters**:
- `audio_file_path` (str): Path to the audio file to transcribe

**Returns**:
- `Dict[str, Any]`: Comprehensive transcription data including:
  - `detected_language`: Auto-detected language code
  - `full_text`: Complete transcribed text
  - `total_duration`: Audio duration in seconds
  - `segments`: List of transcribed segments with timestamps
  - `metadata`: Processing metadata

**Process Flow**:
1. Load and preprocess audio (16kHz, mono)
2. Chunk audio into 30-second segments with 2-second overlap
3. Transcribe each chunk using Whisper model
4. Merge segments and remove overlapping words
5. Return comprehensive results

#### `chunk_audio(audio) -> list[tuple[float, float, np.ndarray]]`

Splits audio into manageable chunks for processing.

**Parameters**:
- `audio` (np.ndarray): Audio data as numpy array

**Returns**:
- `list[tuple[float, float, np.ndarray]]`: List of tuples containing:
  - Start time (seconds)
  - End time (seconds)
  - Audio chunk data

**Configuration**:
- Chunk size: 30 seconds
- Overlap: 2 seconds
- Sample rate: 16kHz

#### `remove_overlapping_words(all_words: List[Dict], overlap_threshold: float = 1.5) -> List[Dict]`

Removes duplicate words that occur due to chunk overlap.

**Parameters**:
- `all_words` (List[Dict]): List of word dictionaries with timing information
- `overlap_threshold` (float): Time threshold for considering words as duplicates (default: 1.5 seconds)

**Returns**:
- `List[Dict]`: Filtered list of words with duplicates removed

**Algorithm**:
1. Sort words by start time
2. For each word, check against recent words within threshold
3. Remove words with similar content and timing
4. Return filtered word list

#### `merge_segments(segments: List[Dict]) -> List[Dict]`

Merges transcription segments and removes overlapping words.

**Parameters**:
- `segments` (List[Dict]): List of segment dictionaries from chunk processing

**Returns**:
- `List[Dict]`: Merged segments with overlapping words removed

**Process**:
1. Collect all words from all segments
2. Remove overlapping words using `remove_overlapping_words`
3. Reconstruct segments based on filtered words
4. Merge segments with gaps less than 2 seconds
5. Calculate average confidence scores

#### `save_transcription_to_json(transcription_data: Dict[str, Any], output_path: str) -> None`

Saves transcription data to a JSON file.

**Parameters**:
- `transcription_data` (Dict[str, Any]): Transcription data to save
- `output_path` (str): Path where to save the JSON file

**Usage**:
```python
from app.services.stt_service import transcribe_audio, save_transcription_to_json

# Transcribe audio
result = transcribe_audio("audio.wav")

# Save to file
save_transcription_to_json(result, "transcription.json")
```

## Configuration

### Model Configuration

The STT module uses the Whisper Large model configured through the model loader service.

**Environment Variables**:
- `WHISPER_MODEL_NAME`: Model name (default: "whisper-large")
- `MODEL_CACHE_DIR`: Directory for model caching
- `SAMPLE_RATE`: Audio sample rate (default: 16000)

### Audio Processing Configuration

**Chunking Parameters**:
- Chunk size: 30 seconds
- Overlap: 2 seconds
- Sample rate: 16kHz (fixed)

**Overlap Removal**:
- Overlap threshold: 1.5 seconds
- Gap threshold: 2.0 seconds

### File Handling Configuration

**Supported Formats**:
- MP3: `audio/mpeg`, `audio/mp3`
- WAV: `audio/wav`, `audio/wave`, `audio/x-wav`
- WebM: `audio/webm`

**Temporary File Handling**:
- Files saved with proper extensions
- Automatic cleanup after processing
- Error handling for cleanup failures

## Usage Examples

### Basic Transcription

```python
from app.services.stt_service import transcribe_audio

# Simple transcription
result = transcribe_audio("sample.wav")
print(f"Text: {result['full_text']}")
print(f"Language: {result['detected_language']}")
print(f"Duration: {result['total_duration']} seconds")
```

### Advanced Usage with Segments

```python
from app.services.stt_service import transcribe_audio

# Get detailed segment information
result = transcribe_audio("long_audio.mp3")

for segment in result['segments']:
    print(f"Segment: {segment['start']:.1f}s - {segment['end']:.1f}s")
    print(f"Text: {segment['text']}")
    print(f"Confidence: {segment['confidence']:.2f}")
    
    # Word-level details
    for word in segment['words']:
        print(f"  {word['word']}: {word['start']:.1f}s-{word['end']:.1f}s (conf: {word['confidence']:.2f})")
    print()
```

### Batch Processing

```python
import os
from app.services.stt_service import transcribe_audio, save_transcription_to_json

def process_audio_directory(input_dir, output_dir):
    """Process all audio files in a directory."""
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.wav', '.mp3', '.webm')):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.json")
            
            try:
                print(f"Processing {filename}...")
                result = transcribe_audio(input_path)
                save_transcription_to_json(result, output_path)
                print(f"Saved transcription to {output_path}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

# Usage
process_audio_directory("audio_files/", "transcriptions/")
```

### Real-time Processing Simulation

```python
import time
from app.services.stt_service import transcribe_audio

def process_with_progress(audio_file):
    """Process audio with progress indication."""
    print("Starting transcription...")
    start_time = time.time()
    
    result = transcribe_audio(audio_file)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"Transcription completed in {processing_time:.2f} seconds")
    print(f"Audio duration: {result['total_duration']:.2f} seconds")
    print(f"Processing speed: {result['total_duration']/processing_time:.2f}x real-time")
    print(f"Chunks processed: {result['metadata']['chunks_processed']}")
    
    return result

# Usage
result = process_with_progress("long_audio.wav")
```

## Error Handling

### Common Error Scenarios

#### File Format Errors

**Error**: `File must be an audio file in MP3, WAV, or WebM format`

**Causes**:
- Unsupported file format
- Missing or incorrect content-type header
- Corrupted file

**Solutions**:
- Ensure file is in supported format
- Check file extension matches content
- Verify file is not corrupted

#### Audio Processing Errors

**Error**: `Transcription failed: [specific error]`

**Common Causes**:
- Corrupted audio file
- Unsupported audio encoding
- Insufficient memory
- Model loading failure

**Solutions**:
- Verify audio file integrity
- Convert to supported format
- Check system resources
- Restart service if model loading fails

#### Memory Errors

**Error**: `Out of memory` or similar

**Causes**:
- Very large audio files
- Insufficient system memory
- Memory leaks in processing

**Solutions**:
- Process smaller chunks
- Increase system memory
- Monitor memory usage
- Restart service periodically

### Error Handling Best Practices

```python
import logging
from app.services.stt_service import transcribe_audio

def safe_transcribe(audio_file_path):
    """Transcribe audio with comprehensive error handling."""
    logger = logging.getLogger(__name__)
    
    try:
        # Validate file exists
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        # Check file size
        file_size = os.path.getsize(audio_file_path)
        if file_size > 100 * 1024 * 1024:  # 100MB limit
            raise ValueError(f"File too large: {file_size} bytes")
        
        # Attempt transcription
        result = transcribe_audio(audio_file_path)
        
        # Validate result
        if not result.get('full_text'):
            raise ValueError("No text transcribed")
        
        return result
        
    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        raise
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise
    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        raise
```

## Performance Considerations

### Processing Performance

**Factors Affecting Performance**:
- Audio file duration
- Audio quality and complexity
- System resources (CPU, memory)
- Model loading time

**Typical Performance**:
- Processing speed: 2-5x real-time (depending on hardware)
- Memory usage: ~2-4GB for Whisper Large model
- First request: Slower due to model loading
- Subsequent requests: Faster with cached model

### Optimization Strategies

#### For Large Files

```python
# Process in smaller chunks for very large files
def process_large_file(audio_file_path, max_chunk_duration=300):
    """Process large audio files with size limits."""
    # Check file duration first
    import librosa
    duration = librosa.get_duration(filename=audio_file_path)
    
    if duration > max_chunk_duration:
        print(f"Warning: File duration ({duration:.1f}s) exceeds recommended limit ({max_chunk_duration}s)")
        print("Consider splitting the file for better performance")
    
    return transcribe_audio(audio_file_path)
```

#### Memory Management

```python
import gc
from app.services.stt_service import transcribe_audio

def transcribe_with_cleanup(audio_file_path):
    """Transcribe with explicit memory cleanup."""
    try:
        result = transcribe_audio(audio_file_path)
        return result
    finally:
        # Force garbage collection
        gc.collect()
```

### Scaling Considerations

**Current Limitations**:
- Single-threaded processing
- In-memory model caching
- No distributed processing

**Future Improvements**:
- Multi-threaded chunk processing
- Distributed model serving
- Streaming audio processing
- GPU acceleration

## Troubleshooting

### Common Issues

#### Model Loading Issues

**Problem**: Model fails to load on startup

**Symptoms**:
- Service fails to start
- "Model unavailable" errors
- Long startup times

**Solutions**:
1. Check internet connection for model download
2. Verify sufficient disk space
3. Check model cache directory permissions
4. Restart service

#### Audio Quality Issues

**Problem**: Poor transcription accuracy

**Symptoms**:
- Incorrect or missing words
- Low confidence scores
- Language detection errors

**Solutions**:
1. Use higher quality audio files
2. Ensure proper sample rate (16kHz recommended)
3. Reduce background noise
4. Use clear speech
5. Check audio format compatibility

#### Performance Issues

**Problem**: Slow transcription processing

**Symptoms**:
- Long processing times
- High memory usage
- System slowdown

**Solutions**:
1. Check system resources
2. Use smaller audio files
3. Restart service to clear memory
4. Monitor system performance
5. Consider hardware upgrades

### Debugging Tools

#### Enable Debug Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add debug information
logger.debug(f"Processing audio file: {audio_file_path}")
logger.debug(f"File size: {os.path.getsize(audio_file_path)} bytes")
logger.debug(f"Audio duration: {duration} seconds")
```

#### Performance Monitoring

```python
import time
import psutil
from app.services.stt_service import transcribe_audio

def monitor_transcription(audio_file_path):
    """Monitor transcription performance."""
    # Get initial memory usage
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    start_time = time.time()
    
    try:
        result = transcribe_audio(audio_file_path)
        
        end_time = time.time()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"Processing time: {end_time - start_time:.2f} seconds")
        print(f"Memory usage: {initial_memory:.1f}MB -> {final_memory:.1f}MB")
        print(f"Memory increase: {final_memory - initial_memory:.1f}MB")
        
        return result
        
    except Exception as e:
        print(f"Error during transcription: {e}")
        raise
```

### Getting Help

If you encounter issues not covered in this documentation:

1. Check the application logs for detailed error messages
2. Verify your audio file format and quality
3. Ensure system resources are sufficient
4. Try with a smaller test file first
5. Contact the development team with:
   - Error messages
   - Audio file details (format, size, duration)
   - System specifications
   - Steps to reproduce the issue

## Future Enhancements

### Planned Features

1. **Real-time Streaming**: WebSocket support for live audio transcription
2. **Batch Processing**: Multiple file processing endpoints
3. **Custom Models**: Support for fine-tuned Whisper models
4. **Language Selection**: Manual language specification
5. **Output Formats**: Support for SRT, VTT subtitle formats
6. **Speaker Diarization**: Identify different speakers
7. **Punctuation Enhancement**: Improved punctuation and formatting

### Performance Improvements

1. **GPU Acceleration**: CUDA support for faster processing
2. **Model Quantization**: Reduced memory usage
3. **Streaming Processing**: Process audio as it's received
4. **Caching**: Cache transcription results
5. **Load Balancing**: Distribute processing across multiple instances

### Integration Features

1. **Webhook Support**: Notify external systems of completion
2. **Database Storage**: Store transcription history
3. **User Management**: Per-user transcription limits
4. **API Versioning**: Support for multiple API versions
5. **Rate Limiting**: Prevent abuse and ensure fair usage
