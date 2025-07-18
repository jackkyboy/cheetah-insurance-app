import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import axios from "axios";
import "../assets/styles/FiltersBar.css";

const FiltersBar = ({ onApplyFilters, initialFilters = {} }) => {
  const [filters, setFilters] = useState({
    company_name: "",
    insurance_type: "",
    repair_type: "",
    ...initialFilters,
  });

  const [options, setOptions] = useState({
    companies: [],
    insuranceTypes: [],
    repairTypes: [],
  });

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        console.log("📤 Fetching filter options...");
        const [companyRes, insuranceRes, repairRes] = await Promise.all([
          axios.get("http://localhost:5000/api/filter-packages/options"),
          axios.get("http://localhost:5000/api/multi-step-search/get_insurance_types"),
          axios.get("http://localhost:5000/api/multi-step-search/get_repair_types"),
        ]);

        const companies = [
          ...new Set(companyRes?.data?.map((item) => item.company_name)),
        ].filter(Boolean);

        const insuranceTypes = (insuranceRes?.data?.insurance_types || []).filter((t) =>
          ["1", "2", "2+", "3", "3+"].includes(t)
        );

        const repairTypes = (repairRes?.data?.repair_types || []).filter((r) =>
          ["ซ่อมอู่", "ซ่อมห้าง"].includes(r)
        );

        setOptions({ companies, insuranceTypes, repairTypes });
      } catch (err) {
        console.error("❌ Failed to fetch filter options:", err);
        setOptions({ companies: [], insuranceTypes: [], repairTypes: [] });
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const handleApplyFilters = () => {
    console.log("🔍 Applying Filters:", filters);
    onApplyFilters(filters);
  };

  const handleClearFilters = () => {
    const cleared = { company_name: "", insurance_type: "", repair_type: "" };
    setFilters(cleared);
    onApplyFilters(cleared);
    console.log("❌ Cleared Filters");
  };

  const renderSelect = (label, name, optionsArray) => (
    <div className="form-group">
      <label>{label}:</label>
      <select name={name} value={filters[name]} onChange={handleInputChange}>
        <option value="">-- เลือก{label.toLowerCase()} --</option>
        {optionsArray.map((opt, i) => (
          <option key={i} value={opt}>
            {opt}
          </option>
        ))}
      </select>
    </div>
  );

  return (
    <div className="filters-bar">
      <h2 className="filters-title">🔍 ค้นหาประกันภัย</h2>
      {loading && <p className="loading-text">⏳ กำลังโหลดข้อมูล...</p>}

      <div className="filters-grid">
        {renderSelect("บริษัทประกันภัย", "company_name", options.companies)}
        {renderSelect("ประเภทประกันภัย", "insurance_type", options.insuranceTypes)}
        {renderSelect("ประเภทการซ่อม", "repair_type", options.repairTypes)}
      </div>

      <div className="button-group">
        <button className="apply-filters-btn" onClick={handleApplyFilters}>
          🔎 ใช้ตัวกรอง
        </button>
        <button className="clear-filters-btn" onClick={handleClearFilters}>
          ❌ ล้างค่า
        </button>
      </div>
    </div>
  );
};

FiltersBar.propTypes = {
  onApplyFilters: PropTypes.func.isRequired,
  initialFilters: PropTypes.object,
};

export default FiltersBar;
