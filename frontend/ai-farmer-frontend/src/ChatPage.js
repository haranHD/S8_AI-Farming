import React, { useState, useRef, useEffect } from "react";
import WeatherCard from "./WeatherCard";
import MarketHeader from "./MarketHeader";
import MarketPricesCard from "./MarketPricesCard";

import farmImg from "./image/farm.png";
import speakerIcon from "./image/speaker.png";
import micIcon from "./image/mic.png";
import cameraIcon from "./image/camera.png";

import "./ChatLayout.css";
import "./ChatPage.css";

const ChatPage = () => {
  const [input, setInput] = useState("");
  const [language, setLanguage] = useState("English");

  // 🛒 MARKET STATES
  const [showMarket, setShowMarket] = useState(false);
  const [crop, setCrop] = useState("");
  const [price, setPrice] = useState("");
  const [quantity, setQuantity] = useState("");
  const [seller, setSeller] = useState("");
  const [marketItems, setMarketItems] = useState([]);

  const getWelcomeMessage = (lang) =>
    lang === "Tamil"
      ? "🌾 வரவேற்கிறோம் விவசாயி!"
      : "🌾 Welcome farmer!";

  const [messages, setMessages] = useState([
    { sender: "bot", text: getWelcomeMessage("English") }
  ]);

  // =========================
  // 🔥 CAMERA FIX (NEW)
  // =========================
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);
  const [showCameraOptions, setShowCameraOptions] = useState(false);
  const handleImage = async (file) => {
    if (!file) return;

    const formData = new FormData();
    formData.append("image", file);
    formData.append("message", "");

    try {
      const res = await fetch("http://localhost:5001/chat", {
        method: "POST",
        body: formData
      });

      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        { sender: "user", text: "📷 Image sent" },
        { sender: "bot", text: data.reply }
      ]);
    } catch (err) {
      console.error(err);
      alert("Image upload failed");
    }
  };

  const openCameraOptions = () => {
    setShowCameraOptions((prev) => !prev);
  };

  const openUpload = () => {
    fileInputRef.current.click();
    setShowCameraOptions(false);
  };

  const openCamera = () => {
    cameraInputRef.current.click();
    setShowCameraOptions(false);
  };
  // =========================
  // 🛒 FETCH MARKET
  // =========================
  const fetchMarket = async () => {
    const res = await fetch("http://localhost:5001/buy");
    const data = await res.json();
    setMarketItems(data.items || []);
  };

  // =========================
  // 🛒 SELL ITEM
  // =========================
  const sellItem = async () => {
    if (!crop || !price || !quantity || !seller) {
      alert("Fill all fields");
      return;
    }

    await fetch("http://localhost:5001/sell", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ crop, price, quantity, seller })
    });

    setCrop("");
    setPrice("");
    setQuantity("");
    setSeller("");

    fetchMarket();
  };

  // =========================
  // 🛒 BUY ITEM
  // =========================
  const handleBuy = async (item) => {
    try {
      const res = await fetch(`http://localhost:5001/buy/${item._id}`, {
        method: "DELETE"
      });

      const data = await res.json();

      if (res.ok) {
        alert("✅ Item purchased successfully!");
        fetchMarket();
      } else {
        alert("❌ Failed to purchase item");
      }

    } catch (err) {
      console.error(err);
      alert("❌ Server error while buying");
    }
  };

  // 🎙️ MIC
  const startListening = () => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) return alert("Not supported");

    const recognition = new SpeechRecognition();
    recognition.lang = language === "Tamil" ? "ta-IN" : "en-IN";

    recognition.onresult = (e) => {
      setInput(e.results[0][0].transcript);
    };

    recognition.start();
  };

  // 🔊 SPEAK
  const speakText = async (text) => {

    // ✅ ENGLISH → use browser (FAST)
    if (language === "English") {
      const speech = new SpeechSynthesisUtterance(text);
      speech.lang = "en-IN";
      speech.rate = 1;
      speech.pitch = 1;

      window.speechSynthesis.speak(speech);
      return;
    }

    // ✅ TAMIL → use backend (gTTS)
    try {
      const res = await fetch("http://localhost:5001/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          message: text,
          language: "Tamil",
          speak: true
        })
      });

      const data = await res.json();

      if (data.audio) {
        const audio = new Audio(`data:audio/mp3;base64,${data.audio}`);
        audio.play();
      } else {
        alert("Speech not available");
      }

    } catch (err) {
      console.error("TTS Error:", err);
    }
  };
  // 💬 SEND MESSAGE
  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);

    const res = await fetch("http://localhost:5001/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        message: input,
        language: language   // ✅ VERY IMPORTANT
      })
    });

    const data = await res.json();

    setMessages((prev) => [
      ...prev,
      { sender: "bot", text: data.reply }
    ]);

    setInput("");
  };

  return (
    <div className="app-wrapper">

      <div className="language-select-box">
        <select value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="English">English</option>
          <option value="Tamil">Tamil</option>
        </select>
      </div>

      <div className="app-grid">
        <header className="header">
          <MarketHeader />
        </header>

        <aside className="sidebar">
          <WeatherCard />
          <MarketPricesCard />
        </aside>

        <main className="main">
          <div className="chat-box">

            <div className="chat-header">
              <img src={farmImg} alt="" className="chat-header-img" />
              <span>Farm AI</span>
            </div>

            {/* MARKET */}
            <button
              className="market-toggle-btn"
              onClick={() => {
                setShowMarket(!showMarket);
                fetchMarket();
              }}
            >
              🛒 Marketplace
            </button>

            {showMarket && (
              <div className="market-box">
                <h3>Sell Crop</h3>

                <div className="market-form">
                  <input placeholder="Crop" value={crop} onChange={(e) => setCrop(e.target.value)} />
                  <input placeholder="Price" value={price} onChange={(e) => setPrice(e.target.value)} />
                  <input placeholder="Qty" value={quantity} onChange={(e) => setQuantity(e.target.value)} />
                  <input placeholder="Seller" value={seller} onChange={(e) => setSeller(e.target.value)} />
                  <button onClick={sellItem}>Sell</button>
                </div>

                <h3>Available Crops</h3>

                {marketItems.map((item, i) => (
                  <div key={i} className="market-item">
                    <div>
                      🌾 <strong>{item.crop}</strong>
                      <div>₹{item.price} • {item.quantity} kg</div>
                      <div>👤 {item.seller}</div>
                    </div>

                    <button className="buy-btn" onClick={() => handleBuy(item)}>
                      Buy
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* CHAT */}
            <div className="chat-messages">
              {messages.map((msg, i) => (
                <div key={i} className={`message ${msg.sender}`}>
                  {msg.text}

                  {msg.sender === "bot" && (
                    <button
                      className="speaker-btn"
                      onClick={() => speakText(msg.text)}
                    >
                      <img src={speakerIcon} alt="" />
                    </button>
                  )}
                </div>
              ))}
            </div>

            {/* INPUT */}
            <div className="chat-input">

              {/* CAMERA BUTTON FIXED */}
              <div style={{ position: "relative", display: "inline-block" }}>
                <button className="ui-icon" onClick={openCameraOptions}>
                  <img src={cameraIcon} alt="" />
                </button>

                {showCameraOptions && (
                  <div
                    style={{
                      position: "absolute",
                      bottom: "45px",
                      left: "0",
                      background: "#ffffff",
                      padding: "6px",
                      borderRadius: "10px",
                      boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
                      zIndex: 999,
                      display: "flex",
                      flexDirection: "column",
                      gap: "6px",
                      minWidth: "120px"
                    }}
                  >
                    <button
                      onClick={openUpload}
                      style={{
                        padding: "6px",
                        border: "none",
                        background: "#f2f2f2",
                        borderRadius: "6px",
                        cursor: "pointer"
                      }}
                    >
                      📁 Upload
                    </button>

                    <button
                      onClick={openCamera}
                      style={{
                        padding: "6px",
                        border: "none",
                        background: "#f2f2f2",
                        borderRadius: "6px",
                        cursor: "pointer"
                      }}
                    >
                      📸 Camera
                    </button>
                  </div>
                )}
              </div>

              <button className="ui-icon" onClick={startListening}>
                <img src={micIcon} alt="" />
              </button>

              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
              // onKeyDown={(e) => { }
              />

              <button className="send-btn" onClick={sendMessage}>
                ➤
              </button>
            </div>

            {/* Hidden Inputs */}
            <input
              type="file"
              accept="image/*"
              ref={fileInputRef}
              style={{ display: "none" }}
              onChange={(e) => handleImage(e.target.files[0])}
            />

            <input
              type="file"
              accept="image/*"
              capture
              ref={cameraInputRef}
              style={{ display: "none" }}
              onChange={(e) => handleImage(e.target.files[0])}
            />

          </div>
        </main>
      </div >
    </div >
  );
};

export default ChatPage;