import os
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
REMOTE_API_KEY = os.getenv("GITHUB_TOKEN")
if not REMOTE_API_KEY:
    raise RuntimeError("GITHUB_TOKEN not set")

app = Flask(__name__)

REMOTE_URL = "https://models.github.ai/inference"
REMOTE_MODEL = "openai/gpt-4.1-nano"

LOCAL_URL = "http://host.docker.internal:1234/v1"
LOCAL_COMPLETION_MODEL = "qwen/qwen3-vl-4b"
LOCAL_EMBEDDING_MODEL = "text-embedding-jina-embeddings-v2-base-de"

LOCAL_API_KEY = "lm-studio"

remote_client = OpenAI(api_key=REMOTE_API_KEY, base_url=REMOTE_URL)
local_client = OpenAI(api_key=LOCAL_API_KEY, base_url=LOCAL_URL)

# chat completions
def get_completion_from_model(client: OpenAI, model: str, messages: dict) -> str:
    response = client.chat.completions.create(model=model, messages=messages)
    return str(response.choices[0].message.content)

def get_completion(remote_model: str, local_model: str, messages: dict) -> dict:
    try:
        response = get_completion_from_model(remote_client, remote_model, messages)
        print(f"Using remote for inference, selected model '{remote_model}'")
        return {"text": response}
    except Exception as e:
        print(f"Local model '{local_model}' used for inference, because of error '{e}'")
        return {"text": get_completion_from_model(local_client, local_model, messages)}

def extract_models(models) -> tuple: 
    if not isinstance(models, dict):
        return REMOTE_MODEL, LOCAL_COMPLETION_MODEL
    
    if "remote" not in models:
        models["remote"] = REMOTE_MODEL
    
    if "local" not in models:
        models["local"] = LOCAL_COMPLETION_MODEL
    
    return models["remote"], models["local"]


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
    remote_model, local_model = extract_models(
        data.get(
            "model",
            {
                "local": LOCAL_COMPLETION_MODEL, 
                "remote": REMOTE_MODEL,
            }
        )
    )
    messages = data.get("messages", [])
    return jsonify(get_completion(remote_model, local_model, messages))

@app.route("/v1/embeddings", methods=["POST"])
def embedding():
    data = request.get_json(force=True)
    model = data.get("model", LOCAL_EMBEDDING_MODEL)
    input = data.get("input", "")
    return jsonify(get_embedding(model, input))


if __name__ == "__main__":
    app.run("0.0.0.0", port=8001, debug=True)