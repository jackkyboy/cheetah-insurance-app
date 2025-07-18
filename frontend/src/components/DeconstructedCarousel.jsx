// 📁 src/components/DeconstructedCarousel.jsx
import React from "react";
import { useNavigate } from "react-router-dom";
import "../assets/styles/DeconstructedCarousel.css";

const DeconstructedCarousel = ({ packages }) => {
  const navigate = useNavigate();

  return (
    <div className="carousel">
      <div className="carousel-track">
        {packages.map((pkg, index) => {
          const {
            company_logo = "/gallery_logos/partners/default-logo.svg",
            company_full_name = "ไม่ระบุบริษัท",
            insurance_type,
            car_brand,
            car_model_year,
            car_model,
            car_submodel,
            premium,
            package_code,
          } = pkg;

          const gradientId = `gradient-${index}`;

          return (
            <article
              key={index}
              className="deconstructed-card ocean-content"
              onMouseMove={(e) => {
                const card = e.currentTarget;
                const rect = card.getBoundingClientRect();
                const x = (e.clientX - rect.left) / rect.width;
                const y = (e.clientY - rect.top) / rect.height;
                const xDeg = (y - 0.5) * 8;
                const yDeg = (x - 0.5) * -8;
                card.style.transform = `perspective(1200px) rotateX(${xDeg}deg) rotateY(${yDeg}deg)`;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "";
              }}
            >
              {/* SVG Wave Background */}
              <div className="card-layer card-image">
                <svg className="wave-svg" viewBox="0 0 300 400" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="#118AB2" />
                      <stop offset="100%" stopColor="#5AC8E3" />
                    </linearGradient>
                  </defs>
                  <rect width="100%" height="100%" fill={`url(#${gradientId})`} />
                </svg>
              </div>

              {/* Card Frame */}
              <div className="card-layer card-frame">
                <svg viewBox="0 0 300 400" preserveAspectRatio="none">
                  <path className="frame-path" d="M 20,20 H 280 V 380 H 20 Z" />
                </svg>
              </div>

              {/* Card Content */}
              <div className="card-layer card-content">
                <div className="content-fragment fragment-heading">
                  <h2 className="content-text">{company_full_name}</h2>
                  <h3 className="content-subtext">ชั้น {insurance_type || "-"}</h3>
                </div>

                <div className="content-fragment fragment-meta">
                  <div className="meta-line"></div>
                  <span className="meta-text">
                    {car_brand || "-"} • {car_model_year || "-"}
                  </span>
                </div>

                <div className="content-fragment fragment-body">
                  <p className="content-text">
                    รุ่น: {car_model || "-"} / {car_submodel || "-"} <br />
                    เบี้ยรวม:{" "}
                    {premium ? `${parseFloat(premium).toLocaleString()} บาท` : "N/A"}
                  </p>
                </div>

                <div className="content-fragment fragment-cta">
                  <button
                    className="cta-link"
                    onClick={() =>
                      navigate(`/package/${package_code}`, {
                        state: { packageData: pkg },
                      })
                    }
                  >
                    <div className="cta-box"></div>
                    <span className="cta-text">📄 ดูรายละเอียด</span>
                  </button>
                </div>
              </div>
            </article>
          );
        })}
      </div>
    </div>
  );
};

export default DeconstructedCarousel;
