# Hybrid OpenAI-Compatible Inference Proxy

## Overview

This project is a **Flask-based API proxy** that provides an OpenAI-compatible interface for:

- Chat completions with automatic fallback, endpoint `/v1/chat/completions`
- Embeddings (local-only), endpoint `/v1/embeddings`
- Health checks, endpoint `/v1/heartbeat`

It attempts to use GitHub Models for inference first and falls back to a local LM Studio–compatible server if GitHub inference fails due to rate limits for example.

## Availabe Model Providers

### GitHub Models (Primary)
- Model: `openai/gpt-4.1-nano` (fixed)
- Endpoint: `https://models.github.ai/inference`
- Auth: `GITHUB_TOKEN`

Please note, that embeddings are not available for GitHub models.

### Local Models (Fallback for Chat Completions and Embeddings)
- Chat Completion: `qwen/qwen3-vl-4b` by default, other models can be selected using the `model` parameter
- Embeddings: `text-embedding-jina-embeddings-v2-base-de` by default, other models can be selected using the `model` parameter
- Endpoint: `http://host.docker.internal:1234/v1`
- Auth: no access token needed

## Endpoints

### Heartbeat

This endpoint does not take any parameters and accepts both `POST` and `GET` requests. The result is

```json
{
  "message": "running"
}
```

### Chat Completions

This endpoint accepts `POST` requests of the following form:

```json
{
  "model": "qwen/qwen3-vl-4b",
  "messages": [
    { "role": "system", "content": "You are helpful." },
    { "role": "user", "content": "Hello!" }
  ]
}
```

The result looks like this:
```json
{
  "text": "Hello! How can I help you today?"
}
```

### Embeddings

This endpoint accepts `POST` requests of the following form:

```json
{
  "model": "text-embedding-jina-embeddings-v2-base-de",
  "input": "Some text"
}
```

The result just contains the embedding vector as list of floats.
```json
[0.0123, -0.9821, 0.4412, ...]
```

## Requirements

- Python 3.9+
- GitHub Models access
- Local inference server (optional but recommended)

Python Dependencies:

```bash
pip install flask openai python-dotenv
```

The GitHub access token must be set by

```bash
export GITHUB_TOKEN=your_github_models_api_key
```

## Running the Service

The service is started with the following command:

```bash
python app.py
```

The service will start on `http://localhost:8001`.