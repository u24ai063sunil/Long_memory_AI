import axios from "axios";
import { getSessionId } from "../utils/session";

const API = axios.create({
    baseURL: "http://localhost:8000",
});

export async function sendMessage(message) {
    const session_id = getSessionId();

    const res = await API.post("/chat", {
        session_id,
        message,
    });

    return res.data;
}
