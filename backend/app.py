from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import uuid
import numpy as np
from PIL import Image
from tensorflow.keras.applications.mobilenet_v2 import (
    MobileNetV2,
    preprocess_input,
    decode_predictions
)
from pymongo import MongoClient
import bcrypt
from bson import ObjectId

# =========================
# MONGODB
# =========================
client = MongoClient("mongodb://localhost:27017/")
db = client["farming_chatbot"]
market_collection = db["marketplace"]
users_collection = db["users"]

# =========================
# MODEL
# =========================
model = MobileNetV2(weights="imagenet")

# =========================
# ENV
# =========================
load_dotenv()
app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# =========================
# REGISTER
# =========================
@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()

        name = data.get("name")
        phone = data.get("phone")
        password = data.get("password")

        # validation
        if not name or not phone or not password:
            return jsonify({"message": "Missing fields"}), 400

        # check if user exists
        if users_collection.find_one({"phone": phone}):
            return jsonify({"message": "User already exists"}), 400

        # hash password
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        users_collection.insert_one({
            "name": name,
            "phone": phone,
            "password": hashed_pw
        })

        return jsonify({"message": "Registration successful"}), 201

    except Exception as e:
        print("REGISTER ERROR:", e)
        return jsonify({"error": "Register failed"}), 500


# =========================
# LOGIN (USERNAME BASED)
# =========================
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()

        name = data.get("name")
        password = data.get("password")

        # validation
        if not name or not password:
            return jsonify({"message": "Missing fields"}), 400

        user = users_collection.find_one({"name": name})

        if not user:
            return jsonify({"message": "User not found"}), 404

        stored_password = user["password"]

        # safe bcrypt handling
        if isinstance(stored_password, str):
            stored_password = stored_password.encode("utf-8")
        elif isinstance(stored_password, bytes):
            pass
        else:
            stored_password = bytes(stored_password)

        if bcrypt.checkpw(password.encode("utf-8"), stored_password):
            return jsonify({
                "message": "Login successful",
                "user": {
                    "name": user["name"],
                    "phone": user["phone"]
                }
            }), 200

        return jsonify({"message": "Invalid password"}), 401

    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({"error": "Login failed"}), 500


# =========================
# WEATHER API
# =========================
@app.route("/weather", methods=["GET"])
def get_weather():
    try:
        city = request.args.get("city", "Erode").strip()

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        res = requests.get(url, timeout=10)
        data = res.json()

        if "main" not in data:
            return jsonify({"error": "Weather not found"}), 404

        return jsonify({
            "city": city,
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"]
        })

    except Exception as e:
        print("WEATHER ERROR:", e)
        return jsonify({"error": "Weather failed"}), 500

#========================
# MARKET PRICES (AI GENERATED)
#========================
@app.route("/market-prices", methods=["GET"])
def market_prices():
    try:
        prompt = """
        Give today's daily crop market prices in India.
        Format:
        crop name - price per kg (INR)
        Only 8 major crops.
        """

        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "You are an agriculture market analyst"},
                {"role": "user", "content": prompt}
            ]
        }

        res = requests.post(url, headers=headers, json=payload)
        data = res.json()

        reply = data["choices"][0]["message"]["content"]

        return jsonify({"prices": reply})

    except Exception as e:
        print("MARKET PRICE ERROR:", e)
        return jsonify({"error": "Failed to fetch prices"}), 500
# =========================
# SELL
# =========================
@app.route("/sell", methods=["POST"])
def sell_crop():
    try:
        data = request.get_json()

        item = {
            "crop": data.get("crop"),
            "price": data.get("price"),
            "quantity": data.get("quantity"),
            "seller": data.get("seller")
        }

        result = market_collection.insert_one(item)

        return jsonify({
            "message": "Item added",
            "id": str(result.inserted_id)
        })

    except Exception as e:
        print("SELL ERROR:", e)
        return jsonify({"error": "Sell failed"}), 500


# =========================
# BUY LIST
# =========================
@app.route("/buy", methods=["GET"])
def buy_crops():
    try:
        items = list(market_collection.find())

        for item in items:
            item["_id"] = str(item["_id"])

        return jsonify({"items": items})

    except Exception as e:
        print("BUY ERROR:", e)
        return jsonify({"error": "Fetch failed"}), 500


# =========================
# BUY ITEM (DELETE)
# =========================
@app.route("/buy/<item_id>", methods=["DELETE"])
def buy_item(item_id):
    try:
        result = market_collection.delete_one({"_id": ObjectId(item_id)})

        if result.deleted_count == 0:
            return jsonify({"error": "Item not found"}), 404

        return jsonify({"message": "Item purchased successfully"})

    except Exception as e:
        print("BUY ERROR:", e)
        return jsonify({"error": "Failed to buy item"}), 500


# =========================
# CHAT + IMAGE
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        if request.content_type and "multipart/form-data" in request.content_type:
            user_message = request.form.get("message", "").strip()
            image = request.files.get("image")
        else:
            data = request.get_json()
            user_message = data.get("message", "").strip()
            image = None

        if not user_message and not image:
            return jsonify({"reply": "Send message or image"})

        # ================= IMAGE =================
        if image:
            os.makedirs("uploads", exist_ok=True)

            filename = str(uuid.uuid4()) + ".jpg"
            path = os.path.join("uploads", filename)
            image.save(path)

            disease = predict_disease(path)

            if disease == "unknown":
                return jsonify({"reply": "Try clearer plant image 🌿"})

            if disease == "not_plant":
                return jsonify({"reply": "Not a plant ❌"})

            prompt = f"Detected: {disease}. Explain simply for farmers."

            url = "https://api.groq.com/openai/v1/chat/completions"

            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "Farming expert"},
                    {"role": "user", "content": prompt}
                ]
            }

            res = requests.post(url, headers=headers, json=payload)
            data = res.json()

            reply = data["choices"][0]["message"]["content"]

            return jsonify({"reply": f"📸 {disease}\n\n{reply}"})

        # ================= TEXT CHAT =================
        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "Simple farming assistant"},
                {"role": "user", "content": user_message}
            ]
        }

        res = requests.post(url, headers=headers, json=payload)
        data = res.json()

        return jsonify({
            "reply": data["choices"][0]["message"]["content"]
        })

    except Exception as e:
        print("CHAT ERROR:", e)
        return jsonify({"reply": "Server error"}), 500


# =========================
# IMAGE MODEL
# =========================
def predict_disease(path):
    try:
        img = Image.open(path).convert("RGB")
        img = img.resize((224, 224))
        img = np.array(img)

        img = preprocess_input(img)
        img = np.expand_dims(img, axis=0)

        preds = model.predict(img)
        decoded = decode_predictions(preds, top=1)[0][0]

        label = decoded[1]
        confidence = round(decoded[2] * 100, 2)

        if confidence < 25:
            return "unknown"

        if any(x in label for x in ["car", "dog", "person"]):
            return "not_plant"

        return f"{label} ({confidence}%)"

    except:
        return "unknown"


# =========================
# RUN
# =========================
if __name__ == "__main__":
    print("Server running http://127.0.0.1:5001")
    app.run(debug=True, port=5001)