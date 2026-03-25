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

  const handleAuth = (e) => {
    e.preventDefault();
    // After successful login or register, redirect to chat page
    navigate("/chat");
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
          {!isLogin && <input type="password" placeholder="Confirm Password" required />}
          <button type="submit">{isLogin ? "LOGIN" : "REGISTER"}</button>
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
