import React, { useState, useEffect } from "react";
import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";
import "./styles/chat.css";

function App() {

  // VERY IMPORTANT: session id for memory
  const [sessionId] = useState(() => {
    let id = localStorage.getItem("session_id");
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem("session_id", id);
    }
    return id;
  });

  const [messages, setMessages] = useState([]);
  const [typing, setTyping] = useState(false);

  const sendMessage = async (text) => {

    if (!text.trim()) return;

    const userMsg = { sender: "user", text };
    setMessages(prev => [...prev, userMsg]);

    setTyping(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          session_id: sessionId,
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
        text: "Server connection failed."
      }]);
    }

    setTyping(false);
  };

  return (
    <div className="app">
      <div className="header">
        🧠 Long-Term Memory AI Assistant
      </div>

      <ChatWindow messages={messages} typing={typing} />

      <ChatInput onSend={sendMessage} />
    </div>
  );
}

export default App;
