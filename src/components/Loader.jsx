// /Users/apichet/Downloads/cheetah-insurance-app/src/components/Loader.jsx
// src/components/Loader.jsx
// src/components/Loader.jsx
import React from "react";
import "../assets/styles/Loader.css";

const Loader = ({ message = "กำลังโหลดข้อมูล..." }) => {
  return (
    <div className="loader-wrapper">
      <div className="loader">
        <svg viewBox="0 0 50 50">
          <circle
            className="loader-circle"
            cx="25"
            cy="25"
            r="20"
            strokeWidth="5"
            fill="none"
          />
        </svg>
      </div>
      <p className="loader-text">{message}</p>
    </div>
  );
};

export default Loader;
