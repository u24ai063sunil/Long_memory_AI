import React from "react";

const MessageBubble = ({ message }) => {

  const isUser = message.sender === "user";

  return (
    <div className={`bubble-row ${isUser ? "user-row" : "bot-row"}`}>
      
      {/* Bot Avatar */}
      {!isUser && (
        <div className="bot-avatar">
          <span className="bot-icon">🧠</span>
        </div>
      )}
      
      <div className={`bubble ${isUser ? "user-bubble" : "bot-bubble"}`}>
        {message.text}

        {message.memory && message.memory.length > 0 && (
          <div className="memory-tag">
            <span className="memory-icon">💾</span>
            <span>Memory recalled</span>
          </div>
        )}
      </div>
      
    </div>
  );
};

export default MessageBubble;
