from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

print("GROQ KEY LOADED:", bool(GROQ_API_KEY))
print("WEATHER KEY LOADED:", bool(WEATHER_API_KEY))


# =========================
# WEATHER API
# =========================
@app.route("/weather", methods=["GET"])
def get_weather():
    try:
        city = request.args.get("city", "Erode").strip()

        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={WEATHER_API_KEY}&units=metric"
        )

        res = requests.get(url, timeout=10)
        data = res.json()

        if "main" not in data or "weather" not in data:
            return jsonify({"error": "Weather data not found"}), 404

        return jsonify({
            "city": city,
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"]
        })

    except Exception as e:
        print("WEATHER ERROR:", e)
        return jsonify({"error": "Weather service failed"}), 500


# =========================
# NORMAL CHAT
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "Please type a message."})

        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a friendly farming assistant for South Indian farmers. "
                        "Give practical, reliable farming information. "
                        "Do not guess. Keep answers short and simple."
                    )
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()

        if "choices" not in result:
            return jsonify({"reply": "AI service unavailable."})

        return jsonify({
            "reply": result["choices"][0]["message"]["content"]
        })

    except Exception as e:
        print("CHAT ERROR:", e)
        return jsonify({"reply": "Server error"}), 500


# =========================
# HELPER: SCRAPE MARKET TEXT
# =========================
def scrape_market_text(location):
    driver = None
    try:
        search_query = f"{location} agmarknet market price today tamil nadu"

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(options=options)

        # Simple Google search page scraping fallback
        driver.get(f"https://www.google.com/search?q={search_query}")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        page_text = driver.find_element(By.TAG_NAME, "body").text

        # keep only smaller useful chunk
        lines = [line.strip() for line in page_text.split("\n") if line.strip()]
        filtered = []

        for line in lines:
            low = line.lower()
            if any(word in low for word in [
                "price", "market", "mandi", "agmarknet", "commodity",
                "tomato", "onion", "paddy", "coconut", "turmeric", "cotton"
            ]):
                filtered.append(line)

        market_text = "\n".join(filtered[:30])
        return market_text[:2500]

    except Exception as e:
        print("SCRAPE ERROR:", e)
        return ""
    finally:
        if driver:
            driver.quit()


# =========================
# HELPER: GROQ SUMMARY
# =========================
def get_market_summary(location, language, market_text):
    try:
        if not market_text:
            if language.lower() == "tamil":
                return "இந்த இடத்திற்கான சந்தை தகவல் தற்போது கிடைக்கவில்லை."
            return "Market information is currently unavailable for this location."

        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        prompt = f"""
            Location: {location}
            Language: {language}

            Based on the market text below, give a SHORT and CLEAR farmer update.

            STRICT RULES:
            - Maximum 5 lines only
            - Each line should be a separate point
            - Focus only on important crops
            - Mention price range ONLY if clearly available
            - If no price, just say "market active" or "price moderate"
            - Do NOT repeat information
            - Keep it very simple for farmers
            - If Tamil → full Tamil

            FORMAT:
            - Crop name + short info
            - Example:
            Tomato - price moderate
            Onion - high demand

            Market text:
            {market_text}
            """

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "You are a helpful agriculture assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()

        print("MARKET SUMMARY RAW:", result)

        if "choices" in result:
            return result["choices"][0]["message"]["content"]

        if language.lower() == "tamil":
            return "சந்தை சுருக்கம் தற்போது கிடைக்கவில்லை."
        return "Market summary unavailable."

    except Exception as e:
        print("SUMMARY ERROR:", e)
        if language.lower() == "tamil":
            return "சந்தை சுருக்கம் உருவாக்க முடியவில்லை."
        return "Could not generate market summary."


# =========================
# MARKET ROUTE
# =========================
@app.route("/market", methods=["GET"])
def market_prices():
    try:
        location = request.args.get("location", "Erode").strip()
        language = request.args.get("language", "English").strip()

        market_text = scrape_market_text(location)
        summary = get_market_summary(location, language, market_text)

        return jsonify({
            "location": location,
            "language": language,
            "summary": summary,
            "raw_market_text": market_text
        })

    except Exception as e:
        print("MARKET ERROR:", e)
        return jsonify({
            "location": request.args.get("location", "Erode"),
            "language": request.args.get("language", "English"),
            "summary": "Market service failed.",
            "raw_market_text": ""
        }), 200


# =========================
# RUN
# =========================
if __name__ == "__main__":
    print("Backend starting on http://127.0.0.1:5001")
    app.run(debug=True, port=5001)