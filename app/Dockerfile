# Build argument to control CUDA usage
ARG USE_CUDA=false

# Base image for non-CUDA builds
FROM python:3.12-slim as base-no-cuda

# Base image for CUDA builds  
FROM nvidia/cuda:12.2-devel-ubuntu22.04 as base-with-cuda

# Select the appropriate base image based on USE_CUDA argument
FROM base-no-cuda as base

# Install system dependencies in a single layer
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/home/appuser" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser

# Create the home directory and set proper permissions
RUN mkdir -p /home/appuser && chown -R appuser:appuser /home/appuser

# Set up Hugging Face cache directory
RUN mkdir -p /home/appuser/.cache/huggingface && chown -R appuser:appuser /home/appuser/.cache

# Set environment variables for Hugging Face cache
ENV HF_HOME=/home/appuser/.cache/huggingface
ENV TRANSFORMERS_CACHE=/home/appuser/.cache/huggingface/transformers
ENV HF_DATASETS_CACHE=/home/appuser/.cache/huggingface/datasets

# Copy Poetry configuration files FIRST for better layer caching
COPY pyproject.toml poetry.lock ./

# Configure Poetry: Don't create virtual environment (we're in a container)
RUN poetry config virtualenvs.create false

# Install dependencies using Poetry (this layer will be cached if dependencies don't change)
RUN poetry install --only=main --no-interaction --no-ansi --no-root

# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container (this layer changes most frequently)
COPY . .

# Expose the port that the application listens on.
EXPOSE 6060

# Run the application.
CMD uvicorn 'app.main:app' --host=0.0.0.0 --port=6060
