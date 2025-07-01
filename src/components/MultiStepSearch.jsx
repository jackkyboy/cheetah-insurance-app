/*/Users/apichet/Downloads/cheetah-insurance-app/src/components/MultiStepSearch.jsx*/
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import useCarData from "../hooks/useCarData";
import {
  fetchInsuranceTypes,
  fetchRepairTypes,
  fetchCarBrands,
  fetchAvailableOptions,
} from "../api/multiStepSearchService";
import "../assets/styles/MultiStepSearch.css";

const MultiStepSearch = ({
  onSearch,
  fetchCarModels,
  fetchSubModels,
  fetchCarModelYears,
  insuranceTypes: insuranceTypesProp,
}) => {
  // State ข้อมูลฟอร์ม
  const [formData, setFormData] = useState({
    carBrand: "",
    carModel: "",
    carModelYear: "",
    carSubModel: "",
    insuranceType: "1",
    repairType: "ซ่อมอู่",
  });

  // State อื่น ๆ
  const [step, setStep] = useState(0);
  const [carBrands, setCarBrands] = useState([]);
  const [insuranceTypes, setInsuranceTypes] = useState([]);
  const [repairTypes, setRepairTypes] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  // Hooks สำหรับดึงข้อมูลโมเดลย่อย
  const {
    carModels,
    subModels,
    carModelYears,
    fetchModels,
    fetchSubModelsData,
    fetchYears,
  } = useCarData({ fetchCarModels, fetchSubModels, fetchCarModelYears });

  const navigate = useNavigate();

  // โหลดข้อมูลเบื้องต้นเมื่อ component mount หรือ insuranceTypesProp เปลี่ยน
  useEffect(() => {
    const loadInitialData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [brandsRes, repairRes] = await Promise.all([
          fetchCarBrands(),
          fetchRepairTypes(),
        ]);
        setCarBrands(brandsRes?.length ? brandsRes : ["Toyota", "Honda"]);
        setRepairTypes(repairRes?.length ? repairRes : ["ซ่อมอู่", "ซ่อมห้าง"]);
        setInsuranceTypes(
          insuranceTypesProp?.length
            ? insuranceTypesProp
            : ["1", "2", "2+", "3", "3+"]
        );
      } catch (err) {
        console.error("❌ [MultiStepSearch] Error loading data:", err);
        setError("เกิดข้อผิดพลาดในการโหลดข้อมูล");
      } finally {
        setLoading(false);
      }
    };
    loadInitialData();
  }, [insuranceTypesProp]);

  // กำหนดลำดับขั้นตอนและ options สำหรับแต่ละขั้น
  const steps = [
    { label: "ยี่ห้อรถยนต์", field: "carBrand", options: carBrands },
    { label: "รุ่นรถยนต์", field: "carModel", options: carModels },
    { label: "รุ่นย่อย (ถ้ามี)", field: "carSubModel", options: subModels },
    { label: "ปีรถยนต์", field: "carModelYear", options: carModelYears },
    { label: "ประเภทประกันภัย", field: "insuranceType", options: insuranceTypes },
    { label: "ประเภทการซ่อม", field: "repairType", options: repairTypes },
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
            {s.options?.length > 0 ? (
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
