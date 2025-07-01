import React, { useState } from "react";
import InsurancePopup from "./InsurancePopup";
import "../assets/styles/InsurancePage.css";

const InsurancePage = () => {
  const [popupType, setPopupType] = useState(null);

  const openPopup = (type) => setPopupType(type);
  const closePopup = () => setPopupType(null);

  const cards = [
    { type: "1", label: "ประกันภัยประเภท 1" },
    { type: "2", label: "ประกันภัยประเภท 2" },
    { type: "3", label: "ประกันภัยประเภท 3" },
    { type: "2+", label: "ประกันภัยประเภท 2+" },
    { type: "3+", label: "ประกันภัยประเภท 3+" },
  ];

  return (
    <div>
      <h1>เลือกประเภทประกันภัยภาคสมัครใจ</h1>
      <div className="card-container">
        {cards.map((card) => (
          <div
            key={card.type}
            className="card"
            onClick={() => openPopup(card.type)}
          >
            <h3>{card.label}</h3>
          </div>
        ))}
      </div>

      {popupType && <InsurancePopup type={popupType} onClose={closePopup} />}
    </div>
  );
};

export default InsurancePage;
