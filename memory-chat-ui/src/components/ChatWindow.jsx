import React, { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";

const ChatWindow = ({ messages, typing }) => {

  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  return (
    <div className="chat-window">
      
      {/* Empty State */}
      {messages.length === 0 && !typing && (
        <div className="empty-state">
          <div className="empty-icon">🧠</div>
          <h2 className="empty-title">How can I help you today?</h2>
          <p className="empty-subtitle">
            I'm here to assist with anything you need
          </p>
          
          <div className="suggested-prompts">
            <div className="prompt-label">Try asking:</div>
            <div className="prompt-item">"Help me brainstorm ideas for my project"</div>
            <div className="prompt-item">"Explain quantum computing in simple terms"</div>
            <div className="prompt-item">"Write a professional email"</div>
          </div>
        </div>
      )}
      
      {/* Messages */}
      {messages.map((msg, index) => (
        <MessageBubble key={index} message={msg} />
      ))}

      {typing && <TypingIndicator />}

      <div ref={endRef}></div>
    </div>
  );
};

export default ChatWindow;
