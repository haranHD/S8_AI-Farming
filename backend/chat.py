import requests

API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

def chat_with_gemini(user_message):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        # "HTTP-Referer": "https://farmer-ai.local",  # NOT localhost
        "X-Title": "Farmer AI Assistant"
    }

    payload = {
        "model": "google/gemini-2.0-flash-exp",
        "messages": [
            {"role": "system", "content": "You are an AI assistant for farmers."},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 300
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    print("STATUS:", response.status_code)
    print("RAW RESPONSE:", response.text)

    if response.status_code != 200:
        return None

    return response.json()["choices"][0]["message"]["content"]


if __name__ == "__main__":
    print(chat_with_gemini("How to improve soil fertility for rice farming?"))
