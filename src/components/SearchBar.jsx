/*/Users/apichet/Downloads/cheetah-insurance-app/src/components/SearchBar.jsx */
import React, { useState } from "react";
import "../assets/styles/SearchBar.css";

const SearchBar = ({ onSearch, carBrands, carModels, subModels, insuranceTypes }) => {
  const [formData, setFormData] = useState({
    carBrand: "",
    carModel: "",
    carSubModel: "",
    carModelYear: "",
    insuranceType: "",
  });

  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
      ...(name === "carBrand" && { carModel: "", carSubModel: "" }), // Reset dependent fields
      ...(name === "carModel" && { carSubModel: "" }), // Reset submodel if model changes
    }));
  };

  const handleSearch = async () => {
    const { carBrand, carModel, carModelYear, insuranceType } = formData;

    if (!carBrand || !carModel || !carModelYear || !insuranceType) {
      alert("กรุณากรอกข้อมูลให้ครบทุกช่องที่จำเป็น!");
      console.error("❌ Missing required fields:", formData);
      return;
    }

    const payload = {
      car_brand: carBrand,
      car_model: carModel,
      car_submodel: formData.carSubModel || null,
      car_model_year: carModelYear,
      insurance_type: insuranceType,
    };

    setLoading(true);
    try {
      console.log("📤 Sending payload:", payload);

      const response = await fetch("http://127.0.0.1:5000/api/bigquery/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok && data.results) {
        // Filter results to include only those with package_code
        const validResults = data.results.filter((result) => result.package_code);

        if (validResults.length === 0) {
          alert("ไม่พบข้อมูลแพ็คเกจที่มีรหัส (package_code)!");
          console.warn("⚠️ No valid results:", data.results);
          return;
        }

        console.log("✅ Valid results:", validResults);
        onSearch(validResults); // Pass results to SearchResults
      } else {
        alert(data.message || "ไม่พบข้อมูลจากการค้นหา!");
        console.error("❌ API Error:", data.message || "Unknown error");
      }
    } catch (error) {
      console.error("❌ Search error:", error);
      alert("เกิดข้อผิดพลาดในการค้นหา กรุณาลองใหม่อีกครั้ง");
    } finally {
      setLoading(false);
    }
  };

  const renderDropdownOptions = (options, filterKey = null, filterValue = null) =>
    options
      .filter((option) => (filterKey && filterValue ? option[filterKey] === filterValue : true))
      .map((option, index) => (
        <option key={index} value={option.name || option}>
          {option.name || option}
        </option>
      ));

  return (
    <div className="search-bar">
      {/* Car Brand Dropdown */}
      <div className="form-group">
        <label htmlFor="car-brand">ยี่ห้อรถยนต์:</label>
        <select
          id="car-brand"
          name="carBrand"
          value={formData.carBrand}
          onChange={handleInputChange}
        >
          <option value="">-- เลือกยี่ห้อ --</option>
          {renderDropdownOptions(carBrands)}
        </select>
      </div>

      {/* Car Model Dropdown */}
      <div className="form-group">
        <label htmlFor="car-model">รุ่นรถยนต์:</label>
        <select
          id="car-model"
          name="carModel"
          value={formData.carModel}
          onChange={handleInputChange}
          disabled={!formData.carBrand}
        >
          <option value="">-- เลือกรุ่น --</option>
          {renderDropdownOptions(carModels, "brand", formData.carBrand)}
        </select>
      </div>

      {/* Submodel Dropdown */}
      <div className="form-group">
        <label htmlFor="car-submodel">รุ่นย่อย (ถ้ามี):</label>
        <select
          id="car-submodel"
          name="carSubModel"
          value={formData.carSubModel}
          onChange={handleInputChange}
          disabled={!formData.carModel}
        >
          <option value="">-- เลือกรุ่นย่อย --</option>
          {renderDropdownOptions(subModels, "model", formData.carModel)}
        </select>
      </div>

      {/* Car Model Year Input */}
      <div className="form-group">
        <label htmlFor="car-model-year">ปีรถยนต์:</label>
        <input
          id="car-model-year"
          name="carModelYear"
          type="number"
          placeholder="ระบุปีรถยนต์"
          value={formData.carModelYear}
          onChange={handleInputChange}
        />
      </div>

      {/* Insurance Type Dropdown */}
      <div className="form-group">
        <label htmlFor="insurance-type">ประเภทประกันภัย:</label>
        <select
          id="insurance-type"
          name="insuranceType"
          value={formData.insuranceType}
          onChange={handleInputChange}
        >
          <option value="">-- เลือกประเภทประกัน --</option>
          {renderDropdownOptions(insuranceTypes)}
        </select>
      </div>

      {/* Search Button */}
      <button className="search-btn" onClick={handleSearch} disabled={loading}>
        {loading ? "กำลังค้นหา..." : "ค้นหา"}
      </button>
    </div>
  );
};

export default SearchBar;
