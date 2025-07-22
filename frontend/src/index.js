/*/Users/apichet/Downloads/cheetah-insurance-app/frontend/src/index.js */
/*/Users/apichet/Downloads/cheetah-insurance-app/frontend/src/index.js */
// /Users/apichet/Downloads/cheetah-insurance-app/frontend/src/index.js
/* /Users/apichet/Downloads/cheetah-insurance-app/frontend/src/index.js */

// /Users/apichet/Downloads/cheetah-insurance-app/frontend/src/index.js

import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { HashRouter } from "react-router-dom";

// ✅ Startup Log
console.log("✅ ReactDOM starting...");
console.log("🧪 NODE_ENV =", process.env.NODE_ENV);
console.log("🧪 REACT_APP_API_BASE_URL =", process.env.REACT_APP_API_BASE_URL);
console.log("🧪 REACT_APP_API_BASE_URL =", process.env.REACT_APP_API_BASE_URL);

// 🔍 Grab root DOM node
const rootEl = document.getElementById("root");

if (!rootEl) {
  console.error("❌ Cannot find root element with id='root'");
  alert("ไม่พบ <div id='root'> บน HTML หน้าเว็บ — กรุณาตรวจสอบ public/index.html");
} else {
  const root = ReactDOM.createRoot(rootEl);

  // 🔥 Global JS error handler
  window.addEventListener("error", (e) => {
    console.error("🔥 Global JS Error:", e.message, "at", e.filename, ":", e.lineno);
    alert("พบข้อผิดพลาดในการโหลดแอป โปรดเปิด DevTools → Console");
  });

  // 🔥 Unhandled promise rejection
  window.addEventListener("unhandledrejection", (e) => {
    console.error("🚨 Unhandled Promise Rejection:", e.reason);
    alert("เกิดข้อผิดพลาดที่ไม่ได้จับ (Promise) โปรดเปิด Console");
  });

  // ✅ Log that React will render
  console.log("🚀 Rendering App with <HashRouter>...");

  // 🚀 Mount React App
  root.render(
    <React.StrictMode>
      <HashRouter>
        <App />
      </HashRouter>
    </React.StrictMode>
  );
}
