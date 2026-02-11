import React, { useState } from "react";

const ChatInput = ({ onSend }) => {

  const [text, setText] = useState("");

  const send = () => {
    if (!text.trim()) return;
    onSend(text);
    setText("");
  };

  return (
    <div className="input-wrapper">

      <textarea
        rows="1"
        placeholder="Message Memory Assistant..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e)=>{
          if(e.key==="Enter" && !e.shiftKey){
            e.preventDefault();
            send();
          }
        }}
      />

      <button className="send-btn" onClick={send}>
        ➤
      </button>

    </div>
  );
};

export default ChatInput;
