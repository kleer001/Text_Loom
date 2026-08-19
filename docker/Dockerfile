FROM node:26-alpine AS frontend-builder

WORKDIR /app/frontend

COPY src/GUI/package*.json ./
RUN npm ci

COPY src/GUI/ ./
RUN npm run build

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt setup.py README.md ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -e .

COPY src/ ./src/
COPY --from=frontend-builder /app/frontend/dist ./src/GUI/dist

ENV PYTHONPATH=/app/src

RUN groupadd --gid 1000 textloom \
    && useradd --uid 1000 --gid textloom --create-home textloom \
    && mkdir -p /workspace \
    && chown -R textloom:textloom /workspace /app

USER textloom

WORKDIR /app/src

EXPOSE 8000 5173

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
