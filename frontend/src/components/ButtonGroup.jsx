// /Users/apichet/Downloads/cheetah-insurance-app/src/components/ButtonGroup.jsx
import React, { useState, useEffect } from "react";
import { setupThemeToggle } from "../utils/themeToggle"; // ✅ นำเข้า toggle function
import "./styles.css"; // ✅ CSS ที่ใช้ปุ่ม

const ButtonGroup = () => {
  const [inactiveButtons, setInactiveButtons] = useState([]);

  useEffect(() => {
    setupThemeToggle(); // ✅ รอให้ปุ่ม `.btn-toggle` ถูก render แล้วค่อยผูก event
  }, []);

  const toggleButtonState = (index) => {
    setInactiveButtons((prev) =>
      prev.includes(index) ? prev.filter((i) => i !== index) : [...prev, index]
    );
  };

  return (
    <div className="main-container">
      {[...Array(7)].map((_, index) => (
        <button
          key={index}
          className={`btn-md ${inactiveButtons.includes(index) ? "inactive" : ""}`}
          onClick={() => toggleButtonState(index)}
        >
          Button {index + 1}
        </button>
      ))}
      <button className="btn-toggle" title="Toggle Theme">
        🌗 Toggle Theme
      </button>
    </div>
  );
};

export default ButtonGroup;
