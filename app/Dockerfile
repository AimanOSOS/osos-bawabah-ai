# ============================================================
# BAWABAH AI SERVER - DOLPHIN OCR INTEGRATION (CPU-ONLY BUILD)
# ============================================================

# Base image (lightweight Python 3.12)
FROM python:3.12-slim as base

# ------------------------------------------------------------
# Install system dependencies
# ------------------------------------------------------------
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    git \
    ffmpeg \
    vim \
    && rm -rf /var/lib/apt/lists/* && apt-get clean

# ------------------------------------------------------------
# Install Poetry
# ------------------------------------------------------------
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# ------------------------------------------------------------
# Create non-root user
# ------------------------------------------------------------
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/home/appuser" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser && \
    mkdir -p /home/appuser && chown -R appuser:appuser /home/appuser

# ------------------------------------------------------------
# Hugging Face cache setup
# ------------------------------------------------------------
RUN mkdir -p /home/appuser/.cache/huggingface && chown -R appuser:appuser /home/appuser/.cache
ENV HF_HOME=/home/appuser/.cache/huggingface
ENV TRANSFORMERS_CACHE=/home/appuser/.cache/huggingface/transformers
ENV HF_DATASETS_CACHE=/home/appuser/.cache/huggingface/datasets

# ------------------------------------------------------------
# Install Python dependencies
# ------------------------------------------------------------
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false
## Install PyTorch CPU wheels first so Poetry won't pull an incompatible binary
RUN pip install --no-cache-dir \
    torch==2.4.0+cpu \
    torchvision==0.19.0+cpu \
    torchaudio==2.4.0+cpu \
    --extra-index-url https://download.pytorch.org/whl/cpu || true

# Then install project dependencies with Poetry (will use the preinstalled torch)
RUN poetry install --only=main --no-interaction --no-ansi --no-root || true

# Install lightweight CPU-only dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    soundfile \
    opencv-python-headless \
    pymupdf \
    numpy \
    pydantic \
    pydantic-settings \
    pillow \
    sentence-transformers \
    torch==2.4.0+cpu \
    torchvision==0.19.0+cpu \
    torchaudio==2.4.0+cpu \
    requests \
    --extra-index-url https://download.pytorch.org/whl/cpu

# Skip VoxCPM if private
RUN pip install --no-cache-dir voxcpm || echo "⚠️ VoxCPM not found on PyPI – skipping"

# ------------------------------------------------------------
# Clone Dolphin repo and add model weights
# ------------------------------------------------------------
RUN git clone https://github.com/bytedance/Dolphin.git /app/external/Dolphin \
    && rm -rf /app/external/Dolphin/.git

# Copy pre-downloaded Dolphin model weights if available
COPY external/Dolphin/hf_model /app/external/Dolphin/hf_model

# Add Dolphin repo to Python path
ENV PYTHONPATH="/app/external/Dolphin:${PYTHONPATH}"

# Set Dolphin model path (for service code)
ENV DOLPHIN_MODEL_PATH=/app/external/Dolphin/hf_model

# ------------------------------------------------------------
# Switch to appuser and copy project files
# ------------------------------------------------------------
USER appuser
COPY . .

# ------------------------------------------------------------
# Expose port and start FastAPI server
# ------------------------------------------------------------
EXPOSE 6060
CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=6060"]
