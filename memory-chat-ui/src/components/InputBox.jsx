import { useState } from "react";

export default function InputBox({ onSend }) {
    const [message, setMessage] = useState("");

    const handleSend = () => {
        if (!message.trim()) return;
        onSend(message);
        setMessage("");
    };

    const handleKey = (e) => {
        if (e.key === "Enter") handleSend();
    };

    return (
        <div className="input-container">
            <input
                type="text"
                placeholder="Type a message..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKey}
            />
            <button onClick={handleSend}>Send</button>
        </div>
    );
}
