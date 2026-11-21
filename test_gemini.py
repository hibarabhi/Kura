import time
import tomllib
import requests

key = tomllib.load(open(".streamlit/secrets.toml", "rb"))["GEMINI_API_KEY"]
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent"
start = time.time()
r = requests.post(
    url,
    headers={"x-goog-api-key": key},
    json={
        "contents": [{"role": "user", "parts": [{"text": "Say hello in 5 words"}]}],
        "generationConfig": {"thinkingConfig": {"thinkingLevel": "low"}},
    },
    timeout=120,
)
print("STATUS:", r.status_code, "| time:", round(time.time() - start, 1), "seconds")
print(r.text[:600])