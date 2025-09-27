# Architecture Documentation

This document describes the architecture and design patterns used in the Bawabah AI ML models API server.

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Patterns](#architecture-patterns)
- [Component Design](#component-design)
- [Data Flow](#data-flow)
- [Configuration Management](#configuration-management)
- [Error Handling Strategy](#error-handling-strategy)
- [Performance Considerations](#performance-considerations)
- [Scalability Design](#scalability-design)

## System Overview

The Bawabah AI API server is built using a modular, service-oriented architecture that provides a scalable foundation for hosting multiple ML models through REST API endpoints.

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │    │   Web Browser   │    │   API Clients   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │     FastAPI Server        │
                    │   (HTTP/WebSocket)        │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │      Router Layer         │
                    │   (Request Routing)       │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │     Service Layer         │
                    │   (Business Logic)        │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │     Model Layer           │
                    │   (ML Model Loading)      │
                    └───────────────────────────┘
```

## Architecture Patterns

### 1. Layered Architecture

The application follows a clean layered architecture:

- **Presentation Layer**: FastAPI routers handling HTTP requests/responses
- **Business Logic Layer**: Services containing domain logic
- **Data Access Layer**: Model loading and caching
- **Configuration Layer**: Centralized configuration management

### 2. Service-Oriented Architecture (SOA)

Each ML model is encapsulated in its own service:
- **TTS Service**: Text-to-speech functionality
- **Model Loader Service**: Model lifecycle management
- **Future Services**: Image classification, NLP, etc.

### 3. Dependency Injection

Services are injected into routers, promoting:
- Testability
- Loose coupling
- Easy mocking for testing

### 4. Configuration as Code

All configuration is managed through Pydantic models with:
- Environment variable support
- Type validation
- Default values
- Documentation

## Component Design

### Router Layer (`app/routers/`)

**Responsibilities:**
- HTTP request/response handling
- Input validation using Pydantic models
- Error handling and status codes
- API documentation

**Design Principles:**
- Thin controllers (minimal business logic)
- Consistent error responses
- Comprehensive input validation
- Clear API documentation

**Example Structure:**
```python
@router.post("/endpoint")
async def endpoint(request: RequestModel):
    try:
        result = service.process_request(request)
        return ResponseModel(**result)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal error")
```

### Service Layer (`app/services/`)

**Responsibilities:**
- Business logic implementation
- Model interaction
- Data processing
- Error handling

**Design Principles:**
- Single responsibility per service
- Stateless operations
- Comprehensive logging
- Exception handling

**Example Structure:**
```python
def process_data(input_data: InputType) -> OutputType:
    """Process input data using ML models."""
    logger.info(f"Processing data: {type(input_data)}")
    
    try:
        model = get_model()
        result = model.predict(input_data)
        
        logger.info("Processing completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise
```

### Model Layer (`app/services/model_loader.py`)

**Responsibilities:**
- Model loading and initialization
- Model caching
- Resource management
- Model lifecycle

**Design Principles:**
- Lazy loading
- Memory-efficient caching
- Resource cleanup
- Error recovery

**Caching Strategy:**
```python
_model_cache = {}

def get_model(model_name: str):
    """Load and cache model with lazy initialization."""
    if model_name not in _model_cache:
        logger.info(f"Loading model: {model_name}")
        _model_cache[model_name] = load_model(model_name)
        logger.info(f"Model loaded: {model_name}")
    
    return _model_cache[model_name]
```

## Data Flow

### Request Processing Flow

```
1. Client Request
   ↓
2. FastAPI Router
   ├── Request validation
   ├── Authentication (future)
   └── Rate limiting (future)
   ↓
3. Service Layer
   ├── Business logic
   ├── Model interaction
   └── Data processing
   ↓
4. Model Layer
   ├── Model loading/caching
   ├── Inference
   └── Result formatting
   ↓
5. Response
   ├── Data serialization
   ├── Error handling
   └── Logging
```

### TTS Request Flow

```
1. POST /api/v1/text-to-speech/generate
   ↓
2. Router validates JSON request
   ↓
3. TTS Service processes text
   ↓
4. Model Loader provides VoxCPM model
   ↓
5. Model generates audio
   ↓
6. Service formats audio response
   ↓
7. Router returns WAV file
```

### Voice Cloning Flow

```
1. POST /api/v1/text-to-speech/clone
   ↓
2. Router validates multipart form
   ↓
3. TTS Service processes files
   ├── Saves temporary audio file
   ├── Validates audio format
   └── Prepares model inputs
   ↓
4. Model Loader provides VoxCPM model
   ↓
5. Model generates cloned audio
   ↓
6. Service formats response
   ↓
7. Router returns WAV file
   ↓
8. Cleanup temporary files
```

## Configuration Management

### Configuration Architecture

```
Environment Variables
         ↓
    .env File
         ↓
   Pydantic Settings
         ↓
   Type Validation
         ↓
   Application Config
```

### Configuration Classes

```python
class Settings(BaseSettings):
    """Centralized configuration with validation."""
    
    # Model settings
    tts_model_name: str = Field(default="openbmb/VoxCPM-0.5B")
    
    # Validation
    @validator('tts_model_name')
    def validate_model_name(cls, v):
        if not v.strip():
            raise ValueError('Model name cannot be empty')
        return v.strip()
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

### Environment Variable Mapping

```python
fields = {
    "tts_model_name": {"env": "TTS_MODEL_NAME"},
    "debug": {"env": "DEBUG"},
    # ... other mappings
}
```

## Error Handling Strategy

### Error Hierarchy

```
Exception
├── ValidationError (400)
├── AuthenticationError (401) [Future]
├── AuthorizationError (403) [Future]
├── NotFoundError (404) [Future]
├── RateLimitError (429) [Future]
└── InternalError (500)
```

### Error Handling Pattern

```python
try:
    result = process_request(request)
    return result
except ValidationError as e:
    logger.warning(f"Validation error: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
except ModelLoadError as e:
    logger.error(f"Model loading failed: {str(e)}")
    raise HTTPException(status_code=500, detail="Model unavailable")
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal server error")
```

### Logging Strategy

```python
import logging

# Structured logging
logger = logging.getLogger(__name__)

# Log levels
logger.debug("Detailed debugging information")
logger.info("General information about operation")
logger.warning("Warning about potential issues")
logger.error("Error occurred but operation can continue")
logger.critical("Critical error, operation cannot continue")
```

## Performance Considerations

### Model Caching

- **Memory Caching**: Models loaded once and cached in memory
- **Lazy Loading**: Models loaded only when first requested
- **Resource Management**: Proper cleanup of model resources

### Request Processing

- **Async Operations**: FastAPI async/await for concurrent requests
- **Streaming Responses**: Large files streamed to avoid memory issues
- **Connection Pooling**: Efficient database connections (future)

### Resource Optimization

```python
# Efficient model loading
def get_model():
    if model_name not in _model_cache:
        # Load model only when needed
        _model_cache[model_name] = load_model()
    return _model_cache[model_name]

# Memory-efficient file handling
def process_audio_file(file_path: str):
    with tempfile.NamedTemporaryFile() as temp_file:
        # Process file
        result = process_file(temp_file.name)
        # Automatic cleanup
    return result
```

## Scalability Design

### Horizontal Scaling

**Current Limitations:**
- In-memory model caching
- Single instance deployment

**Future Scaling Strategies:**

1. **Load Balancing**
   ```
   Load Balancer
   ├── Instance 1 (Models A, B)
   ├── Instance 2 (Models C, D)
   └── Instance 3 (Models A, C)
   ```

2. **Model Distribution**
   - Different models on different instances
   - Model-specific scaling
   - Resource optimization per model type

3. **Caching Strategy**
   - Redis for distributed model caching
   - CDN for static model files
   - Database for model metadata

### Vertical Scaling

**Resource Optimization:**
- GPU memory management
- CPU optimization
- Memory usage monitoring

### Microservices Architecture (Future)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │    │   TTS Service   │    │  Image Service  │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │    Service Registry       │
                    │   (Discovery & Config)    │
                    └───────────────────────────┘
```

## Security Considerations

### Current Security

- Input validation with Pydantic
- File type validation
- Error message sanitization

### Future Security Enhancements

1. **Authentication**
   - API key authentication
   - JWT tokens
   - OAuth integration

2. **Authorization**
   - Role-based access control
   - Model-specific permissions
   - Rate limiting per user

3. **Data Protection**
   - Input sanitization
   - Output validation
   - Secure file handling

## Monitoring and Observability

### Current Monitoring

- Application logging
- Error tracking
- Basic health checks

### Future Monitoring

1. **Metrics**
   - Request/response times
   - Model inference times
   - Resource usage
   - Error rates

2. **Tracing**
   - Request tracing
   - Model performance tracking
   - Dependency monitoring

3. **Alerting**
   - Error rate thresholds
   - Performance degradation
   - Resource exhaustion

## Deployment Architecture

### Development Environment

```
Developer Machine
├── Python 3.13+
├── Poetry
├── Local .env file
└── Direct model downloads
```

### Production Environment (Future)

```
Production Server
├── Docker containers
├── Environment variables
├── Model pre-loading
├── Health checks
└── Monitoring integration
```

## Future Enhancements

### Planned Features

1. **Additional ML Models**
   - Image classification
   - Natural language processing
   - Computer vision
   - Recommendation systems

2. **Advanced Features**
   - Batch processing
   - WebSocket support
   - Real-time streaming
   - Model versioning

3. **Infrastructure**
   - Kubernetes deployment
   - Auto-scaling
   - Service mesh
   - Distributed caching

### Architecture Evolution

The current monolithic architecture will evolve into a microservices architecture as the system grows, with each ML model becoming its own service for better scalability and maintainability.
