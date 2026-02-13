import React from "react";

const TypingIndicator = () => {
  return (
    <div className="bubble-row bot-row">
      <div className="bot-avatar">
        <span className="bot-icon">🧠</span>
      </div>
      <div className="bubble bot-bubble typing-bubble">
        <div className="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;
