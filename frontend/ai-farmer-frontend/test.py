import requests
import json
import os

# API_KEY = os.getenv("OPENROUTER_API_KEY")

URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer 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",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "Python Test"
}

# ---------- First API Call ----------
payload_1 = {
    "model": "openai/gpt-4o-mini",
    "messages": [
        {
            "role": "user",
            "content": "How many r's are in the word 'strawberry'?"
        }
    ]
}

response1 = requests.post(URL, headers=HEADERS, json=payload_1)
response1.raise_for_status()

assistant_message = response1.json()["choices"][0]["message"]["content"]

# ---------- Second API Call ----------
payload_2 = {
    "model": "openai/gpt-4o-mini",
    "messages": [
        {"role": "user", "content": "How many r's are in the word 'strawberry'?"},
        {"role": "assistant", "content": assistant_message},
        {"role": "user", "content": "Are you sure? Think carefully."}
    ]
}

response2 = requests.post(URL, headers=HEADERS, json=payload_2)
response2.raise_for_status()

print(response2.json()["choices"][0]["message"]["content"])
