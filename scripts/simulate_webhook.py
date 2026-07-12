import random
import requests

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "lcis_-EZ2F3RyPSZzEEGYDYZz8jSdWt6PBHUxH1-NdqXhi8w"
CLIENT_ID = 1
PROJECT_ID = 1

MODELS = [
    ("openai", "gpt-4o"),
    ("openai", "gpt-4o-mini"),
    ("gemini", "gemini-1.5-flash"),
]

def send_event():
    provider, model = random.choice(MODELS)
    payload = {
        "provider": provider,
        "model": model,
        "tokens_used": random.randint(500, 20000),
        "latency": round(random.uniform(0.2, 3.0), 2),
        "client_id": CLIENT_ID,
        "project_id": PROJECT_ID,
        "source": "ingestion:litellm",
    }
    resp = requests.post(
        f"{BASE_URL}/v1/ingest",
        json=payload,
        headers={"X-API-Key": API_KEY},
    )
    print(resp.status_code, resp.json())

if __name__ == "__main__":
    for _ in range(20):
        send_event()