import { v4 as uuidv4 } from "uuid";

export function getSessionId() {
    let sessionId = localStorage.getItem("memory_session_id");

    if (!sessionId) {
        sessionId = uuidv4();
        localStorage.setItem("memory_session_id", sessionId);
    }

    return sessionId;
}
