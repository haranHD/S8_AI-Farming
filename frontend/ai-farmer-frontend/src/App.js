import React, { useState } from "react";
import { Routes, Route, useNavigate } from "react-router-dom";
import ChatPage from "./ChatPage";
import "./App.css";

// Home page after login (optional)
const HomePage = () => (
  <div className="home-container">
    <h1>Welcome to your Farm Assistant 🌱</h1>
  </div>
);

// Login / Register Form
const AuthForm = () => {
  const [isLogin, setIsLogin] = useState(true);
  const navigate = useNavigate();

  const handleAuth = async (e) => {
    e.preventDefault();

    const form = e.target;

    try {
      // ================= LOGIN =================
      if (isLogin) {
        const res = await fetch("http://127.0.0.1:5001/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: form[0].value,
            password: form[1].value,
          }),
        });

        const data = await res.json();

        if (res.ok) {
          alert("Login Successful 🚀");
          navigate("/chat");
        } else {
          alert(data.message || "Login failed");
        }
      }

      // ================= REGISTER =================
      else {
        const res = await fetch("http://127.0.0.1:5001/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: form[0].value,
            phone: form[1].value,
            password: form[2].value,
          }),
        });

        const data = await res.json();

        if (res.ok) {
          alert("Registration Successful 🚀");
          setIsLogin(true);
        } else {
          alert(data.message || "Register failed");
        }
      }
    } catch (error) {
      console.error("API Error:", error);
      alert("Server not responding");
    }
  };

  return (
    <div className="app-container">
      <div className="form-card">
        <h2 className="title">AI Farmer</h2>
        <p className="subtitle">Grow Smarter, Not Harder</p>

        <form onSubmit={handleAuth}>
          <input type="text" placeholder="Username" required />
          {!isLogin && <input type="tel" placeholder="Phone Number" required />}
          <input type="password" placeholder="Password" required />
          {!isLogin && (
            <input type="password" placeholder="Confirm Password" required />
          )}
          <button type="submit">
            {isLogin ? "LOGIN" : "REGISTER"}
          </button>
        </form>

        <p className="switch-text" onClick={() => setIsLogin(!isLogin)}>
          {isLogin
            ? "New user? Create an account"
            : "Already have an account? Login"}
        </p>
      </div>
    </div>
  );
};

// Main App with Routes
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<AuthForm />} />
      <Route path="/home" element={<HomePage />} />
      <Route path="/chat" element={<ChatPage />} />
    </Routes>
  );
}