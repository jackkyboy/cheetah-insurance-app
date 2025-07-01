// /Users/apichet/Downloads/cheetah-insurance-app/src/components/MotorForm.jsx
import React from "react";

const MotorForm = ({ motorData, handleInputChange }) => {
  return (
    <form className="motor-form">
      <h2>ข้อมูลรถยนต์</h2>
      <div className="form-group">
        <label htmlFor="carBrand">ยี่ห้อรถ:</label>
        <input
          id="carBrand"
          type="text"
          name="carBrand"
          placeholder="กรอกยี่ห้อรถ"
          value={motorData.brand}
          onChange={(e) => handleInputChange("motorDetail", "brand", e.target.value)}
        />
      </div>
      <div className="form-group">
        <label htmlFor="carModel">รุ่นรถ:</label>
        <input
          id="carModel"
          type="text"
          name="carModel"
          placeholder="กรอกรุ่นรถ"
          value={motorData.model}
          onChange={(e) => handleInputChange("motorDetail", "model", e.target.value)}
        />
      </div>
      <div className="form-group">
        <label htmlFor="carYear">ปีรถ:</label>
        <input
          id="carYear"
          type="number"
          name="carYear"
          placeholder="กรอกปีรถ"
          value={motorData.year}
          onChange={(e) => handleInputChange("motorDetail", "year", e.target.value)}
        />
      </div>
    </form>
  );
};

export default MotorForm;
