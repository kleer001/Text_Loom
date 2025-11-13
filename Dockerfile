# Multi-stage build for Text Loom
# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY src/GUI/package*.json ./

# Install dependencies
RUN npm install

# Copy frontend source
COPY src/GUI/ ./

# Build the frontend
RUN npm run build

# Stage 2: Python backend with built frontend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt ./
COPY setup.py ./
COPY README.md ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -e .

# Copy application source
COPY src/ ./src/

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist ./src/GUI/dist

# Set PYTHONPATH
ENV PYTHONPATH=/app/src

# Create workspace directory for persistent data
RUN mkdir -p /workspace && \
    chmod 777 /workspace

# Set working directory to src for compatibility
WORKDIR /app/src

# Expose ports
# 8000 for FastAPI backend
# 5173 for Vite dev server (if running in dev mode)
EXPOSE 8000 5173

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Default command: run the backend API server
# For TUI mode, override with: docker run -it textloom python3 TUI/tui_skeleton.py
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
