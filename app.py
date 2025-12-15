import os
from flask import Flask, request, jsonify
from openai import OpenAI, RateLimitError, APIError
from dotenv import load_dotenv

load_dotenv()
GITHUB_API_KEY = os.getenv("GITHUB_TOKEN")
if not GITHUB_API_KEY:
    raise RuntimeError("GITHUB_TOKEN not set")

app = Flask(__name__)

GITHUB_URL = "https://models.github.ai/inference"
GITHUB_MODEL = "openai/gpt-4.1-nano"

LOCAL_URL = "http://host.docker.internal:1234/v1"
LOCAL_COMPLETION_MODEL = "qwen/qwen3-vl-4b"
LOCAL_EMBEDDING_MODEL = "text-embedding-jina-embeddings-v2-base-de"

LOCAL_API_KEY = "lm-studio"

github_client = OpenAI(api_key=GITHUB_API_KEY, base_url=GITHUB_URL)
local_client = OpenAI(api_key=LOCAL_API_KEY, base_url=LOCAL_URL)

# chat completions
def get_completion_from_model(client, model: str, messages: dict) -> str:
    response = client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content

def get_completion(model: str, messages: dict) -> dict:
    try:
        response = get_completion_from_model(github_client, GITHUB_MODEL, messages)
        print(f"Using GitHub for inference, selected model '{GITHUB_MODEL}'")
        return {"text": response}
    except Exception as e:
        print(f"Local model used for inference, because of error '{e}'")
        return {"text": get_completion_from_model(local_client, model, messages)}

# embeddings - local only
def get_embedding(model: str, chunk: str) -> list:
    print("Local model used for embedding")
    response = local_client.embeddings.create(model=model, input=chunk)
    return response.data[0].embedding

# provided routes
@app.route("/v1/heartbeat", methods=["POST", "GET"])
def heartbeat():
    return jsonify({"message": "running"})

@app.route("/v1/chat/completions", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    model = data.get("model", LOCAL_COMPLETION_MODEL)
    messages = data.get("messages", [])
    return jsonify(get_completion(model, messages))

@app.route("/v1/embeddings", methods=["POST"])
def embedding():
    data = request.get_json(force=True)
    model = data.get("model", LOCAL_EMBEDDING_MODEL)
    input = data.get("input", "")
    return jsonify(get_embedding(model, input))


if __name__ == "__main__":
    app.run("0.0.0.0", port=8001, debug=True)