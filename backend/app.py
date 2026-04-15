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
from googletrans import Translator
from gtts import gTTS
import base64
from io import BytesIO
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
translator = Translator()
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
from googletrans import Translator
from gtts import gTTS
import base64
from io import BytesIO
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
translator = Translator()
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
        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "user",
                    "content": "Give 5 Indian crop prices today in this format: crop - price/kg"
                }
            ]
        }

        res = requests.post(url, headers=headers, json=payload)

        # 🔥 DEBUG PRINT
        print("STATUS:", res.status_code)
        print("RESPONSE:", res.text)

        data = res.json()

        if "choices" not in data:
            return jsonify({"error": "Invalid API response"}), 500

        reply = data["choices"][0]["message"]["content"]

        return jsonify({"prices": reply})

    except Exception as e:
        print("MARKET ERROR:", e)
        return jsonify({"error": "Failed"}), 500
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
        # =========================
        # HANDLE REQUEST TYPE
        # =========================
        if request.content_type and "multipart/form-data" in request.content_type:
            user_message = request.form.get("message", "").strip()
            language = request.form.get("language", "English")
            speak = str(request.form.get("speak", "false")).lower() == "true"
            image = request.files.get("image")
        else:
            data = request.get_json()
            user_message = data.get("message", "").strip()
            language = data.get("language", "English")
            speak = str(data.get("speak", False)).lower() == "true"
            image = None

        if not user_message and not image:
            return jsonify({"reply": "Send message or image"})
        # =========================
        # 🔊 DIRECT SPEECH MODE (FINAL FIX)
        # =========================
        if speak:
            try:
                from io import BytesIO
                import base64

                lang_code = "ta" if language == "Tamil" else "en"

                # 👉 SPEAK EXACT MESSAGE (NO AI CALL)
                tts = gTTS(text=user_message, lang=lang_code)

                audio_bytes = BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes.seek(0)

                audio_base64 = base64.b64encode(audio_bytes.read()).decode("utf-8")

                return jsonify({
                    "reply": user_message,
                    "audio": audio_base64
                })

            except Exception as e:
                print("TTS ERROR:", e)
                return jsonify({"reply": user_message})
        # =========================
        # 🌐 TRANSLATE INPUT (Tamil → English)
        # =========================
        if language in ["Tamil", "ta"] and user_message:
            user_message_en = translator.translate(user_message, src="ta", dest="en").text
        else:
            user_message_en = user_message

        # =========================
        # 💬 TEXT CHAT
        # =========================
        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "Simple farming assistant"},
                {"role": "user", "content": user_message_en}
            ]
        }

        res = requests.post(url, headers=headers, json=payload)
        data = res.json()

        reply = data["choices"][0]["message"]["content"]

        # =========================
        # 🌐 TRANSLATE OUTPUT (English → Tamil)
        # =========================
        if language in ["Tamil", "ta"]:
            reply = translator.translate(reply, src="en", dest="ta").text

        # =========================
        # 🔊 TEXT TO SPEECH
        # =========================
        if speak:
            try:
                lang_code = "ta" if language in ["Tamil", "ta"] else "en"

                tts = gTTS(text=reply, lang=lang_code)

                audio_bytes = BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes.seek(0)

                audio_base64 = base64.b64encode(audio_bytes.read()).decode("utf-8")

                return jsonify({
                    "reply": reply,
                    "audio": audio_base64
                })

            except Exception as e:
                print("TTS ERROR:", e)
                return jsonify({"reply": reply})

        # =========================
        # NORMAL RESPONSE
        # =========================
        return jsonify({"reply": reply})

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
        # =========================
        # HANDLE REQUEST TYPE
        # =========================
        if request.content_type and "multipart/form-data" in request.content_type:
            user_message = request.form.get("message", "").strip()
            language = request.form.get("language", "English")
            speak = str(request.form.get("speak", "false")).lower() == "true"
            image = request.files.get("image")
        else:
            data = request.get_json()
            user_message = data.get("message", "").strip()
            language = data.get("language", "English")
            speak = str(data.get("speak", False)).lower() == "true"
            image = None

        if not user_message and not image:
            return jsonify({"reply": "Send message or image"})
        # =========================
        # 🔊 DIRECT SPEECH MODE (FINAL FIX)
        # =========================
        if speak:
            try:
                from io import BytesIO
                import base64

                lang_code = "ta" if language == "Tamil" else "en"

                # 👉 SPEAK EXACT MESSAGE (NO AI CALL)
                tts = gTTS(text=user_message, lang=lang_code)

                audio_bytes = BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes.seek(0)

                audio_base64 = base64.b64encode(audio_bytes.read()).decode("utf-8")

                return jsonify({
                    "reply": user_message,
                    "audio": audio_base64
                })

            except Exception as e:
                print("TTS ERROR:", e)
                return jsonify({"reply": user_message})
        # =========================
        # 🌐 TRANSLATE INPUT (Tamil → English)
        # =========================
        if language in ["Tamil", "ta"] and user_message:
            user_message_en = translator.translate(user_message, src="ta", dest="en").text
        else:
            user_message_en = user_message

        # =========================
        # 💬 TEXT CHAT
        # =========================
        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "Simple farming assistant"},
                {"role": "user", "content": user_message_en}
            ]
        }

        res = requests.post(url, headers=headers, json=payload)
        data = res.json()

        reply = data["choices"][0]["message"]["content"]

        # =========================
        # 🌐 TRANSLATE OUTPUT (English → Tamil)
        # =========================
        if language in ["Tamil", "ta"]:
            reply = translator.translate(reply, src="en", dest="ta").text

        # =========================
        # 🔊 TEXT TO SPEECH
        # =========================
        if speak:
            try:
                lang_code = "ta" if language in ["Tamil", "ta"] else "en"

                tts = gTTS(text=reply, lang=lang_code)

                audio_bytes = BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes.seek(0)

                audio_base64 = base64.b64encode(audio_bytes.read()).decode("utf-8")

                return jsonify({
                    "reply": reply,
                    "audio": audio_base64
                })

            except Exception as e:
                print("TTS ERROR:", e)
                return jsonify({"reply": reply})

        # =========================
        # NORMAL RESPONSE
        # =========================
        return jsonify({"reply": reply})

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