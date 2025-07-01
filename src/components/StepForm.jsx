import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  fetchCarBrands,
  fetchCarModels,
  fetchCarYears,
  fetchCMIPackages,
  fetchInsuranceCompanies,
} from "../api/carService";
import "../assets/styles/StepForm.css";

const StepForm = () => {
  const [formData, setFormData] = useState({
    vehicleType: "",
    carBrand: "",
    carModel: "",
    carModelYear: "",
    insuranceCompany: "",
    usageType: "ส่วนตัว",
    seatingCapacity: "",
    engineCC: "",
    area: "กรุงเทพฯ",
  });

  const [options, setOptions] = useState({
    vehicleTypes: ["รถจักรยานยนต์", "รถยนต์นั่ง", "รถบรรทุก", "รถพ่วง"],
    usageTypes: ["ส่วนตัว", "เพื่อการพาณิชย์"],
    areas: ["กรุงเทพฯ", "นอกเขต"],
    carBrands: [],
    carModels: [],
    carModelYears: [],
    insuranceCompanies: [],
    seatingCapacities: ["2", "4", "5", "7", "10"],
    engineCCs: ["1000", "1500", "2000", "2500", "3000"],
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const loadInitialData = async () => {
      setLoading(true);
      try {
        const [brands, companies] = await Promise.all([
          fetchCarBrands(),
          fetchInsuranceCompanies(),
        ]);
        setOptions((prev) => ({
          ...prev,
          carBrands: brands || [],
          insuranceCompanies: companies?.results || [],
        }));
      } catch (err) {
        console.error("❌ โหลดข้อมูลเริ่มต้นผิดพลาด:", err);
        setError("ไม่สามารถโหลดข้อมูลได้");
      } finally {
        setLoading(false);
      }
    };
    loadInitialData();
  }, []);

  useEffect(() => {
    if (!formData.carBrand) return;
    const loadCarModels = async () => {
      setLoading(true);
      try {
        const models = await fetchCarModels(formData.carBrand);
        setOptions((prev) => ({
          ...prev,
          carModels: models || [],
          carModelYears: [],
        }));
      } catch (err) {
        console.error("❌ โหลดรุ่นรถผิดพลาด:", err);
        setError("ไม่สามารถโหลดข้อมูลรุ่นรถได้");
      } finally {
        setLoading(false);
      }
    };
    loadCarModels();
  }, [formData.carBrand]);

  useEffect(() => {
    if (!formData.carBrand || !formData.carModel) return;
    const loadCarYears = async () => {
      setLoading(true);
      try {
        const years = await fetchCarYears(formData.carBrand, formData.carModel);
        setOptions((prev) => ({
          ...prev,
          carModelYears: years || [],
        }));
      } catch (err) {
        console.error("❌ โหลดปีรถผิดพลาด:", err);
        setError("ไม่สามารถโหลดข้อมูลปีรถได้");
      } finally {
        setLoading(false);
      }
    };
    loadCarYears();
  }, [formData.carBrand, formData.carModel]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
      ...(name === "carBrand" && { carModel: "", carModelYear: "" }),
      ...(name === "carModel" && { carModelYear: "" }),
    }));
    setError("");
  };

  const handleSearch = async () => {
    setLoading(true);
    try {
      const sanitizedData = {
        ...formData,
        seatingCapacity: parseInt(formData.seatingCapacity, 10) || null,
        engineCC: parseInt(formData.engineCC, 10) || null,
        usageType: formData.usageType || "ส่วนบุคคล",
        area: formData.area || "กรุงเทพฯ",
      };

      if (Object.values(sanitizedData).some((value) => value === null || value === "")) {
        setError("กรุณากรอกข้อมูลให้ครบถ้วน");
        setLoading(false);
        return;
      }

      const response = await fetchCMIPackages(sanitizedData);

      if (response?.results?.length) {
        navigate("/search-results", { state: { results: response.results } });
      } else {
        setError("ไม่พบแพ็กเกจที่ตรงกับข้อมูลที่ระบุ");
      }
    } catch (err) {
      console.error("❌ โหลดแพ็กเกจผิดพลาด:", err);
      setError("ไม่สามารถโหลดแพ็กเกจได้");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form">
      {[
        { label: "ประเภทของรถ", name: "vehicleType", options: options.vehicleTypes },
        { label: "ประเภทการใช้งาน", name: "usageType", options: options.usageTypes },
        { label: "เขตจดทะเบียน", name: "area", options: options.areas },
        { label: "ยี่ห้อรถ", name: "carBrand", options: options.carBrands },
        { label: "รุ่นรถ", name: "carModel", options: options.carModels },
        { label: "ปีรถ", name: "carModelYear", options: options.carModelYears },
        { label: "บริษัทประกันภัย", name: "insuranceCompany", options: options.insuranceCompanies },
        { label: "จำนวนที่นั่ง", name: "seatingCapacity", options: options.seatingCapacities },
        { label: "CC เครื่องยนต์", name: "engineCC", options: options.engineCCs },
      ].map(({ label, name, options }) => (
        <div className="form-group" key={name}>
          <label>{label}:</label>
          <select name={name} value={formData[name]} onChange={handleChange} disabled={loading}>
            <option value="">{`-- เลือก${label} --`}</option>
            {options.map((option, index) => (
              <option key={index} value={option}>{option}</option>
            ))}
          </select>
        </div>
      ))}
      <button className="search-button" onClick={handleSearch} disabled={loading}>{loading ? "กำลังค้นหา..." : "ค้นหา"}</button>
      {error && <p className="error-message">{error}</p>}
    </div>
  );
};

export default StepForm;
