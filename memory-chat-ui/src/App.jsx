import React, { useState } from "react";
import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";
import Login from "./components/Login";
import "./styles/chat.css";

function App() {

  /* ---------------- USER LOGIN STATE ---------------- */
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("user");
    return saved ? JSON.parse(saved) : null;
  });

  /* ---------------- CHAT STATE ---------------- */
  const [messages, setMessages] = useState([]);
  const [typing, setTyping] = useState(false);

  /* ---------------- SESSION ID (VERY IMPORTANT) ----------------
     Now session is tied to GOOGLE ACCOUNT
     Every user = separate memory database
  */
  const sessionId = user ? user.sub : null;

  /* ---------------- LOGOUT ---------------- */
  const logout = () => {
    localStorage.removeItem("user");
    setUser(null);
    setMessages([]);
  };

  /* ---------------- CLEAR CHAT ---------------- */
  const clearChat = () => {
    setMessages([]);
  };

  /* ---------------- SEND MESSAGE ---------------- */
  const sendMessage = async (text) => {

    if (!text.trim() || !sessionId) return;

    const userMsg = { sender: "user", text };
    setMessages(prev => [...prev, userMsg]);

    setTyping(true);
    const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          session_id: sessionId,   // 🔥 USER BASED MEMORY
          message: text
        })
      });

      const data = await res.json();

      const botMsg = {
        sender: "bot",
        text: data.reply,
        memory: data.used_memory
      };

      setMessages(prev => [...prev, botMsg]);

    } catch (err) {
      setMessages(prev => [...prev, {
        sender: "bot",
        text: "⚠️ Server connection failed. Is FastAPI running?"
      }]);
    }

    setTyping(false);
  };

  /* ---------------- LOGIN SCREEN ---------------- */
  if (!user) return <Login setUser={setUser} />;

  /* ---------------- CHAT UI ---------------- */
  return (
    <div className="app">

      {/* HEADER */}
      <div className="header">

        <div className="title">
          🧠 Memory AI Assistant
        </div>

        <div className="user-area">
          <img src={user.picture} alt="avatar" className="avatar"/>
          <span className="username">{user.name}</span>

          <button className="clear-btn" onClick={clearChat}>
            Clear
          </button>

          <button className="logout-btn" onClick={logout}>
            Logout
          </button>
        </div>

      </div>

      {/* CHAT WINDOW */}
      <ChatWindow messages={messages} typing={typing} />

      {/* INPUT */}
      <ChatInput onSend={sendMessage} />

    </div>
  );
}

export default App;
