import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";

import { GoogleOAuthProvider } from '@react-oauth/google';

const rootElement = document.getElementById("root");
if (!rootElement) throw new Error('Failed to find the root element');

const googleClientId = process.env.REACT_APP_GOOGLE_CLIENT_ID || "";

if (!googleClientId) {
  console.warn("⚠️ REACT_APP_GOOGLE_CLIENT_ID is not set. Google Sign-In will not work.");
}

const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <GoogleOAuthProvider clientId={googleClientId}>
      <App />
    </GoogleOAuthProvider>
  </React.StrictMode>,
);
