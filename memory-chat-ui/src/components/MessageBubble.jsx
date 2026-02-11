import React from "react";

const MessageBubble = ({ message }) => {

  const isUser = message.sender === "user";

  return (
    <div className={`bubble-row ${isUser ? "user" : "bot"}`}>
      <div className={`bubble ${isUser ? "user-bubble" : "bot-bubble"}`}>
        {message.text}

        {message.memory && message.memory.length > 0 && (
          <div className="memory-tag">
            Memory used
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
