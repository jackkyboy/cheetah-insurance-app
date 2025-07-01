// src/components/InfoTooltip.jsx
// src/components/InfoTooltip.jsx
import React, { useState } from "react";
import { AiOutlineInfoCircle } from "react-icons/ai";
import "../assets/styles/InfoTooltip.css";

const InfoTooltip = ({ title, description, position = "top" }) => {
  const [show, setShow] = useState(false);

  const toggleShow = () => setShow((prev) => !prev);

  return (
    <div
      className={`info-tooltip tooltip-${position}`}
      onMouseEnter={() => setShow(true)}
      onMouseLeave={() => setShow(false)}
    >
      <button
        type="button"
        className="info-icon"
        aria-label={`ข้อมูลเพิ่มเติม: ${title}`}
        onClick={toggleShow}
        onFocus={() => setShow(true)}
        onBlur={() => setShow(false)}
      >
        <AiOutlineInfoCircle size={18} />
      </button>

      {show && (
        <div className="tooltip-content" role="tooltip">
          <div className="tooltip-arrow" />
          <div className="tooltip-inner">
            <h4 className="tooltip-title">{title}</h4>
            <p className="tooltip-desc">{description}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default InfoTooltip;
