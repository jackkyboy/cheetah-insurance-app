// /Users/apichet/Downloads/cheetah-insurance-app/src/components/InsurancePopup.jsx
import React from "react";
import PropTypes from "prop-types";
import insuranceDescriptions from "../api/insuranceDescriptions";
import "../assets/styles/InsurancePopup.css";


const InsurancePopup = ({ type, onClose }) => {
  // ดึงข้อมูลของประกันภัยตาม type
  const content = insuranceDescriptions[type] || {
    title: "ไม่พบข้อมูล",
    details: ["ไม่สามารถดึงข้อมูลประกันภัยได้ กรุณาลองใหม่อีกครั้ง"],
  };

  return (
    <div className="popup-overlay">
      <div className="popup-content">
        <h3>{content.title}</h3>
        <ul>
          {content.details.map((detail, index) => (
            <li key={index}>{detail}</li>
          ))}
        </ul>
        <button onClick={onClose} className="close-button">
          ปิด
        </button>
      </div>
    </div>
  );
};

InsurancePopup.propTypes = {
  type: PropTypes.oneOf(["1", "2", "3", "2+", "3+"]).isRequired, // รองรับเฉพาะประเภทที่กำหนด
  onClose: PropTypes.func.isRequired, // ฟังก์ชันสำหรับปิด Popup
};

export default InsurancePopup;
