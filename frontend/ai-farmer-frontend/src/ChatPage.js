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

  const recognitionRef = useRef(null);

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
        fetchMarket(); // refresh list
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
  const speakText = (text) => {
    const speech = new SpeechSynthesisUtterance(text);
    speech.lang = language === "Tamil" ? "ta-IN" : "en-IN";
    window.speechSynthesis.speak(speech);
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
      body: JSON.stringify({ message: input })
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
      {/* LANGUAGE */}
      <div className="language-select-box">
        <select onChange={(e) => setLanguage(e.target.value)}>
          <option>English</option>
          <option>Tamil</option>
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

            {/* HEADER */}
            <div className="chat-header">
              <img src={farmImg} alt="" className="chat-header-img" />
              <span>Farm AI</span>
            </div>

            {/* 🛒 BUTTON */}
            <button
              className="market-toggle-btn"
              onClick={() => {
                setShowMarket(!showMarket);
                fetchMarket();
              }}
            >
              🛒 Marketplace
            </button>

            {/* 🛒 MARKET UI */}
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

                    <button
                      className="buy-btn"
                      onClick={() => handleBuy(item)}
                    >
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
              <button className="ui-icon">
                <img src={cameraIcon} alt="" />
              </button>

              <button className="ui-icon" onClick={startListening}>
                <img src={micIcon} alt="" />
              </button>

              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
              />

              <button className="send-btn" onClick={sendMessage}>
                ➤
              </button>
            </div>

          </div>
        </main>
      </div>
    </div>
  );
};

export default ChatPage;