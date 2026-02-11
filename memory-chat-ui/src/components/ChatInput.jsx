import React, { useState } from "react";

const ChatInput = ({ onSend }) => {

  const [text, setText] = useState("");

  const handleSend = () => {
    onSend(text);
    setText("");
  };

  const handleKey = (e) => {
    if (e.key === "Enter") handleSend();
  };

  return (
    <div className="chat-input">
      <input
        type="text"
        placeholder="Type your message..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKey}
      />
      <button onClick={handleSend}>Send</button>
    </div>
  );
};

export default ChatInput;
