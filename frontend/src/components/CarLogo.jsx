import React from "react";
import PropTypes from "prop-types";
import carLogos from "../assets/carLogos";

const CarLogo = ({ brand, className = "car-logo" }) => {
  // แปลงชื่อแบรนด์ให้เป็น lowercase เพื่อ match กับ key ใน carLogos
  const logoSrc =
    carLogos[brand?.toLowerCase()] || "/assets/car-logos/logos/thumb/default-logo.png";

  return (
    <img
      src={logoSrc}
      alt={`${brand || "ไม่ระบุแบรนด์"} Logo`}
      className={className}
      onError={(e) => {
        console.error(`❌ Error loading logo for brand: ${brand}`);
        e.target.src = "/assets/car-logos/logos/thumb/default-logo.png"; // Fallback logo
      }}
    />
  );
};

CarLogo.propTypes = {
  brand: PropTypes.string.isRequired, // ชื่อแบรนด์รถยนต์ เช่น "Toyota", "BMW"
  className: PropTypes.string, // เพิ่ม className สำหรับการตกแต่งเพิ่มเติม
};

export default CarLogo;
