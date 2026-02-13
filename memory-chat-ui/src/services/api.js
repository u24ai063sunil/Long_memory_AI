import axios from "axios";
import { getSessionId } from "../utils/session";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const API = axios.create({
    baseURL: `${API_URL}`,
});

export async function sendMessage(message) {
    const session_id = getSessionId();

    const res = await API.post("/chat", {
        session_id,
        message,
    });

    return res.data;
}
