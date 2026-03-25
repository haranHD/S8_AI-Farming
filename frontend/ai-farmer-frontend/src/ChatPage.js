import React, { useState, useRef, useEffect } from "react";
import WeatherCard from "./WeatherCard";
import MarketHeader from "./MarketHeader";
import farmImg from "./image/farm.png";
import speakerIcon from "./image/speaker.png";
import micIcon from "./image/mic.png";
import cameraIcon from "./image/camera.png";
import MarketPricesCard from "./MarketPricesCard";
import "./ChatLayout.css";

const ChatPage = () => {
  const [input, setInput] = useState("");
  const [language, setLanguage] = useState("English");

  const getWelcomeMessage = (lang) => {
    return lang === "Tamil"
      ? "🌾 வரவேற்கிறோம் விவசாயி! பயிர்கள், வானிலை, அல்லது சந்தை விலை பற்றி கேளுங்கள்."
      : "🌾 Welcome farmer! Ask me anything about crops, weather, or prices.";
  };

  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: getWelcomeMessage("English")
    }
  ]);

  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  // 🎥 CAMERA STATES
  const [showOptions, setShowOptions] = useState(false);
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const [image, setImage] = useState(null);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    setMessages([
      {
        sender: "bot",
        text: getWelcomeMessage(language)
      }
    ]);
  }, [language]);

  // 🎙️ SPEECH TO TEXT
  const startListening = () => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech Recognition not supported");
      return;
    }

    recognitionRef.current = new SpeechRecognition();
    recognitionRef.current.lang = language === "Tamil" ? "ta-IN" : "en-IN";
    recognitionRef.current.continuous = false;

    setIsListening(true);

    recognitionRef.current.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput((prev) => (prev ? prev + " " + transcript : transcript));
      setIsListening(false);
    };

    recognitionRef.current.onerror = () => {
      setIsListening(false);
    };

    recognitionRef.current.start();
  };

  // 🔊 TEXT TO SPEECH
  const speakText = (text) => {
    if (!window.speechSynthesis) return;

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language === "Tamil" ? "ta-IN" : "en-IN";
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  };

  // 💬 SEND MESSAGE
  const sendMessage = async () => {
    if (!input.trim()) return;

    const userInput = input;
    const userMsg = { sender: "user", text: userInput };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    try {
      const res = await fetch("http://localhost:5001/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userInput,
          language: language
        })
      });

      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: data.reply || "⚠️ No response from AI" }
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text:
            language === "Tamil"
              ? "❌ பின்புற சேவையை அணுக முடியவில்லை"
              : "❌ Backend not reachable"
        }
      ]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") sendMessage();
  };

  // 📷 CAMERA FUNCTIONS
  const openCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;
      setIsCameraOpen(true);
      setShowOptions(false);
    } catch {
      alert(
        language === "Tamil"
          ? "கேமரா அனுமதி மறுக்கப்பட்டது"
          : "Camera permission denied"
      );
    }
  };

  const closeCamera = () => {
    const stream = videoRef.current?.srcObject;
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
    }
    setIsCameraOpen(false);
  };

  const captureImage = () => {
    const canvas = canvasRef.current;
    const video = videoRef.current;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    const imgData = canvas.toDataURL("image/png");
    setImage(imgData);
    closeCamera();
  };

  const handleUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => setImage(reader.result);
    reader.readAsDataURL(file);

    setShowOptions(false);
  };

  return (
    <div className="app-wrapper">
      <div className="language-select-box">
        <label>
          {language === "Tamil" ? "மொழியை தேர்வு செய்க:" : "Select Language:"}
        </label>
        <select value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="English">English</option>
          <option value="Tamil">Tamil</option>
        </select>
      </div>

      <div className="app-grid">
        <header className="header">
          <MarketHeader language={language} />
        </header>

        <aside className="sidebar">
          <WeatherCard language={language} />
          <MarketPricesCard language={language} />
        </aside>

        <main className="main">
          <div className="chat-box">
            <div className="chat-header">
              <img src={farmImg} alt="Farm" className="chat-header-img" />
              <span>
                {language === "Tamil"
                  ? "விவசாய AI உதவியாளர்"
                  : "Farm AI Assistant"}
              </span>
            </div>

            <div className="chat-messages">
              {messages.map((msg, i) => (
                <div key={i} className={`message ${msg.sender}`}>
                  <div>{msg.text}</div>

                  {msg.sender === "bot" && (
                    <button
                      className="speaker-btn"
                      onClick={() => speakText(msg.text)}
                    >
                      <img src={speakerIcon} alt="Speak" />
                    </button>
                  )}
                </div>
              ))}
            </div>

            {image && (
              <div className="image-preview">
                <img src={image} alt="Preview" />
              </div>
            )}

            {isCameraOpen && (
              <div className="camera-box">
                <video ref={videoRef} autoPlay />
                <button onClick={captureImage}>
                  {language === "Tamil" ? "📸 படம் எடு" : "📸 Capture"}
                </button>
                <button onClick={closeCamera}>
                  {language === "Tamil" ? "❌ மூடு" : "❌ Close"}
                </button>
                <canvas ref={canvasRef} style={{ display: "none" }} />
              </div>
            )}

            {showOptions && (
              <div className="camera-options">
                <button onClick={openCamera}>
                  {language === "Tamil" ? "கேமரா திற" : "Open Camera"}
                </button>
                <button onClick={() => fileInputRef.current.click()}>
                  {language === "Tamil" ? "படத்தை பதிவேற்று" : "Upload Image"}
                </button>
                <input
                  type="file"
                  accept="image/*"
                  ref={fileInputRef}
                  onChange={handleUpload}
                  hidden
                />
              </div>
            )}

            <div className="chat-input">
              <button
                className="ui-icon"
                onClick={() => setShowOptions(!showOptions)}
              >
                <img src={cameraIcon} alt="Camera" />
              </button>

              <button
                className={`ui-icon ${isListening ? "listening" : ""}`}
                onClick={startListening}
              >
                <img src={micIcon} alt="Voice" />
              </button>

              <input
                type="text"
                placeholder={
                  language === "Tamil"
                    ? "உங்கள் கேள்வியை টাইப் செய்யவும்..."
                    : "Type a message..."
                }
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
              />

              <button className="send-btn" onClick={sendMessage}>
                ➤
              </button>
            </div>
          </div>
        </main>

        <footer className="footer">
          {language === "Tamil"
            ? "© 2026 Farmer AI • விவசாயிகளுக்கு புத்திசாலித்தனமான உதவி 🌾"
            : "© 2026 Farmer AI • Helping Farmers Grow Smarter 🌾"}
        </footer>
      </div>
    </div>
  );
};

export default ChatPage;