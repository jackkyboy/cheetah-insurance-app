/*/Users/apichet/Downloads/cheetah-insurance-app/src/components/MultiStepSearch.jsx*/
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import useCarData from "../hooks/useCarData";
import {
  fetchCarBrands,
  fetchRepairTypes,
  fetchAvailableOptions,
} from "../api/multiStepSearchService";
import "../assets/styles/MultiStepSearch.css";

// ✅ ป้องกัน .map พัง
const safeArray = (value) => Array.isArray(value) ? value : [];

const MultiStepSearch = ({
  onSearch,
  fetchCarModels,
  fetchSubModels,
  fetchCarModelYears,
  insuranceTypes: insuranceTypesProp,
}) => {
  const navigate = useNavigate();

  // 🧾 Form data state
  const [formData, setFormData] = useState({
    carBrand: "",
    carModel: "",
    carModelYear: "",
    carSubModel: "",
    insuranceType: "1",
    repairType: "ซ่อมอู่",
  });

  // 📦 Option states
  const [step, setStep] = useState(0);
  const [carBrands, setCarBrands] = useState([]);
  const [insuranceTypes, setInsuranceTypes] = useState([]);
  const [repairTypes, setRepairTypes] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  // 🧠 Custom hook สำหรับ fetch ข้อมูลรถ
  const {
    carModels,
    subModels,
    carModelYears,
    fetchModels,
    fetchSubModelsData,
    fetchYears,
  } = useCarData({ fetchCarModels, fetchSubModels, fetchCarModelYears });

  // 🚀 โหลดข้อมูลเริ่มต้น
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [brands, repairs] = await Promise.all([
          fetchCarBrands(),
          fetchRepairTypes(),
        ]);

        setCarBrands(safeArray(brands).length ? brands : ["Toyota", "Honda"]);
        setRepairTypes(safeArray(repairs).length ? repairs : ["ซ่อมอู่", "ซ่อมห้าง"]);
        setInsuranceTypes(
          safeArray(insuranceTypesProp).length
            ? insuranceTypesProp
            : ["1", "2", "2+", "3", "3+"]
        );
      } catch (err) {
        console.error("❌ โหลดข้อมูลเบื้องต้นล้มเหลว:", err);
        setError("เกิดข้อผิดพลาดในการโหลดข้อมูล");
      } finally {
        setLoading(false);
      }
    };

    loadInitialData();
  }, [insuranceTypesProp]);

  // ✅ Steps พร้อมป้องกัน .map พัง
  const steps = [
    { label: "ยี่ห้อรถยนต์", field: "carBrand", options: safeArray(carBrands) },
    { label: "รุ่นรถยนต์", field: "carModel", options: safeArray(carModels) },
    { label: "รุ่นย่อย (ถ้ามี)", field: "carSubModel", options: safeArray(subModels) },
    { label: "ปีรถยนต์", field: "carModelYear", options: safeArray(carModelYears) },
    { label: "ประเภทประกันภัย", field: "insuranceType", options: safeArray(insuranceTypes) },
    { label: "ประเภทการซ่อม", field: "repairType", options: safeArray(repairTypes) },
  ];


  // ฟังก์ชันช่วยรีเซ็ตฟอร์มตาม field ที่เปลี่ยน
  const getResetFields = (fieldName) => {
    switch (fieldName) {
      case "carBrand":
        return { carModel: "", carSubModel: "", carModelYear: "" };
      case "carModel":
        return { carSubModel: "", carModelYear: "" };
      case "carSubModel":
        return { carModelYear: "" };
      default:
        return {};
    }
  };

  // Handler สำหรับเปลี่ยนแปลง input
  const handleInputChange = async (e) => {
    const { name, value } = e.target;

    const resetFields = getResetFields(name);
    const updatedForm = {
      ...formData,
      [name]: value,
      ...resetFields,
    };

    setFormData(updatedForm);

    // โหลดข้อมูล options ตาม step ที่เปลี่ยน
    if (name === "carBrand") {
      fetchModels(value);
    } else if (name === "carModel") {
      fetchSubModelsData(updatedForm.carBrand, value);
    } else if (name === "carSubModel") {
      fetchYears(updatedForm.carBrand, updatedForm.carModel, value);
    }

    // ถ้ามีครบถึง carModelYear ให้ดึง options ที่แมทช์จริงจาก backend
    if (
      updatedForm.carBrand &&
      updatedForm.carModel &&
      updatedForm.carSubModel &&
      updatedForm.carModelYear
    ) {
      setLoading(true);
      try {
        const options = await fetchAvailableOptions({
          car_brand: updatedForm.carBrand,
          car_model: updatedForm.carModel,
          car_submodel: updatedForm.carSubModel,
          year: updatedForm.carModelYear,
        });
        setInsuranceTypes(options.insurance_types || []);
        setRepairTypes(options.repair_types || []);
      } catch (err) {
        console.warn(
          "⚠️ [handleInputChange] Error fetching dynamic filter options:",
          err
        );
      } finally {
        setLoading(false);
      }
    }
  };

  // ปุ่มถัดไป
  const handleNext = () => {
    if (!formData[steps[step].field]) {
      alert(`กรุณากรอกข้อมูล ${steps[step].label}`);
      return;
    }
    setStep((prev) => prev + 1);
  };

  // ปุ่มย้อนกลับ
  const handlePrevious = () => {
    setStep((prev) => Math.max(0, prev - 1));
  };

  // ส่งฟอร์ม (ค้นหา)
  const handleSubmit = () => {
    if (
      !formData.carBrand ||
      !formData.carModel ||
      !formData.carModelYear ||
      !formData.insuranceType
    ) {
      alert("กรุณากรอกข้อมูลให้ครบถ้วน");
      return;
    }

    navigate("/packages", {
      state: {
        filters: {
          car_brand: formData.carBrand,
          car_model: formData.carModel,
          car_submodel: formData.carSubModel,
          year: formData.carModelYear,
          insurance_type: formData.insuranceType,
          repair_type: formData.repairType,
        },
      },
    });
  };

  // UI
  // UI
  return (
    <div id="msform">
      {error && <div className="error">{error}</div>}
      {loading && <div className="loading">กำลังโหลด...</div>}

      <ul id="progressbar">
        {steps.map((s, i) => (
          <li key={i} className={i <= step ? "active" : ""}>
            {s.label}
          </li>
        ))}
      </ul>

      {steps.map((s, i) => (
        <fieldset key={i} className={step === i ? "active" : ""}>
          <h3>{s.label}</h3>
          <select
            name={s.field}
            value={formData[s.field] || ""}
            onChange={handleInputChange}
          >
            <option value="">-- เลือก {s.label} --</option>
            {Array.isArray(s.options) && s.options.length > 0 ? (
              s.options.map((opt, idx) => (
                <option key={idx} value={opt}>
                  {opt}
                </option>
              ))
            ) : (
              <option value="" disabled>
                -- ไม่มีข้อมูล --
              </option>
            )}
          </select>
          <div className="button-group">
            {step > 0 && (
              <button type="button" onClick={handlePrevious}>
                ย้อนกลับ
              </button>
            )}
            {step < steps.length - 1 ? (
              <button type="button" onClick={handleNext}>
                ถัดไป
              </button>
            ) : (
              <button type="button" onClick={handleSubmit}>
                ค้นหา
              </button>
            )}
          </div>
        </fieldset>
      ))}
    </div>
  );
};

export default MultiStepSearch;
