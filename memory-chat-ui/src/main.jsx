import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { GoogleOAuthProvider } from "@react-oauth/google";

// 🔥 CRITICAL: Use environment variable for Google Client ID
// This allows different IDs for development vs production
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

// Error handling: Make sure Client ID is set
if (!GOOGLE_CLIENT_ID) {
  console.error(
    "❌ VITE_GOOGLE_CLIENT_ID is not set! " +
    "Please add it to your .env file or Vercel environment variables."
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <App />
    </GoogleOAuthProvider>
  </React.StrictMode>
);