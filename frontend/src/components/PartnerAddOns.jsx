import React, { useState, useEffect } from "react";
import "../assets/styles/PartnerAddOns.css";

const PartnerAddOns = ({ selectedAddOns, onAddOnChange }) => {
  const [addOns, setAddOns] = useState([]); // รายการ Add-Ons ที่โหลดมาจาก API
  const [expandedAddOn, setExpandedAddOn] = useState(null); // เก็บสถานะเปิด/ปิดของคำอธิบาย

  // ดึงข้อมูล Add-Ons จาก API
  useEffect(() => {
    const fetchAddOns = async () => {
      try {
        const response = await fetch("http://localhost:5000/api/add-ons");
        if (!response.ok) {
          throw new Error("ไม่สามารถโหลดข้อมูล Add-Ons ได้");
        }
        const data = await response.json();
        setAddOns(data.results);
      } catch (error) {
        console.error("❌ Error fetching Add-Ons:", error.message);
      }
    };

    fetchAddOns();
  }, []);

  // ฟังก์ชันจัดการการคลิกเพื่อเปิด/ปิดคำอธิบาย
  const handleToggleDescription = (id) => {
    setExpandedAddOn((prev) => (prev === id ? null : id));
  };

  return (
    <div className="partner-add-ons">
      <h3>แพ็กเกจเสริมจากพาร์ทเนอร์</h3>
      <div className="add-ons-list">
        {addOns.map((addOn) => (
          <div key={addOn.id} className="add-on-card">
            <input
              type="checkbox"
              checked={selectedAddOns.includes(addOn.id)}
              onChange={() => onAddOnChange(addOn.id)}
            />
            <div className="add-on-details">
              <h4>{addOn.name}</h4>
              <p><strong>ราคา:</strong> {addOn.price.toLocaleString()} บาท</p>
              <button
                className="toggle-description-btn"
                onClick={() => handleToggleDescription(addOn.id)}
              >
                {expandedAddOn === addOn.id ? "ซ่อนคำอธิบาย" : "ดูคำอธิบายเพิ่มเติม"}
              </button>
              {expandedAddOn === addOn.id && (
                <div className="add-on-description">
                  <p>{addOn.description}</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PartnerAddOns;
