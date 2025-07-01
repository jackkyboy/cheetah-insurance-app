
//  /Users/apichet/Downloads/cheetah-insurance-app/src/components/FieryInsuranceCard.jsx
// src/components/FieryInsuranceCard.jsx
// src/components/FieryInsuranceCard.jsx
import React, { useEffect, useRef, useId } from "react";
import "../assets/styles/FieryCard.css";
import VanillaTilt from "vanilla-tilt";
import { initFieryRenderer } from "../utils/fieryCardRenderer";

const FieryInsuranceCard = ({ title, price, features, onClick }) => {
  const id = useId();
  const containerRef = useRef(null);
  const canvasRef = useRef(null);
  const tiltRef = useRef(null);

  useEffect(() => {
    const container = containerRef.current;
    const canvas = canvasRef.current;
    const card = tiltRef.current;

    if (!container || !canvas || !card) {
      console.warn("⚠️ Missing container or canvas in FieryInsuranceCard.");
      return;
    }

    // ✅ Initialize tilt effect
    if (!card.vanillaTilt) {
      VanillaTilt.init(card, {
        max: 12,
        speed: 500,
        glare: true,
        "max-glare": 0.25,
        scale: 1.02,
      });
    }

    // ✅ Initialize fire renderer
    initFieryRenderer({ canvas, container });
  }, []);

  return (
    <div className="fiery-container" id={`card-container-${id}`} ref={containerRef}>
      <canvas
        id={`energy-canvas-${id}`}
        ref={canvasRef}
        className="energy-canvas"
        width={400}
        height={400}
      />
      <div className="fiery-card" data-tilt ref={tiltRef}>
        <h2 className="card-title">{title}</h2>
        <p className="card-price">
          <span className="currency">฿</span>{price}
          <span className="period">/ปี</span>
        </p>
        <p className="card-description">
          แพ็กเกจพิเศษ พร้อมความคุ้มครองระดับพรีเมียม
        </p>
        <ul className="features-list">
          {features.map((f, idx) => (
            <li key={idx}>
              <svg className="rotating-disc-svg" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="8" />
              </svg>
              {f}
            </li>
          ))}
        </ul>
        <button className="cta-button" onClick={onClick}>
          ดูรายละเอียด
        </button>
      </div>
    </div>
  );
};

export default FieryInsuranceCard;
