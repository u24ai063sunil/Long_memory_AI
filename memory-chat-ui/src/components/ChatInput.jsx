import React, { useState, useRef, useEffect } from "react";

const ChatInput = ({ onSend }) => {

  const [text, setText] = useState("");
  const textareaRef = useRef(null);

  // Auto-resize textarea as user types
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = textareaRef.current.scrollHeight + "px";
    }
  }, [text]);

  const send = () => {
    if (!text.trim()) return;
    onSend(text);
    setText("");
  };

  return (
    <div className="input-wrapper">
      
      {/* Attach button (optional) */}
      {/* <button className="attach-btn" title="Attach file (coming soon)">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
        </svg>
      </button> */}

      <textarea
        ref={textareaRef}
        rows="1"
        placeholder="Ask me anything... "
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e)=>{
          if(e.key==="Enter" && !e.shiftKey){
            e.preventDefault();
            send();
          }
        }}
        maxLength={2000}
      />

      <button 
        className={`send-btn ${text.trim() ? 'active' : ''}`} 
        onClick={send}
        disabled={!text.trim()}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="22" y1="2" x2="11" y2="13"></line>
          <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
        </svg>
      </button>

    </div>
  );
};

export default ChatInput;