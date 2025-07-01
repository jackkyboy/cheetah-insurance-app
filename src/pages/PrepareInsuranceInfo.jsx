/*/Users/apichet/Downloads/cheetah-insurance-app/src/pages/PrepareInsuranceInfo.jsx */
import React, { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import "../assets/styles/PrepareInsuranceInfo.css";

import { fetchUserProfile } from "../api/userService";
import { saveInsuranceInfo } from "../api/insuranceService";
import InsuranceForm from "../components/InsuranceForm";
import { useAuth } from "../context/AuthContext";

const initialInsuranceData = {
  insured: {
    title: "",
    firstName: "",
    lastName: "",
    idNumber: "",
    birthDate: "",
    age: "",
    mobile: "",
    email: "",
    address: {
      homeNo: "",
      moo: "",
      village: "",
      soi: "",
      road: "",
      tambol: "",
      amphur: "",
      province: "",
      zipCode: "",
    },
  },
  vehicle: {
    licenseNo: "",
    licenseProvince: "",
    chassisNo: "",
    engineNo: "",
    make: "",
    model: "",
    modelYear: "",
    cc: "",
    seat: "",
    weight: "",
  },
  policy: {
    packageCode: "",
    voluntaryClassName: "",
    coverOD: "",
    netGrossPremium: "",
    duty: "",
    tax: "",
    totalPremium: "",
  },
  beneficiary: {
    name: "",
    relationship: "",
  },
};

const PrepareInsuranceInfo = () => {
  const navigate = useNavigate();
  const { user: authUser, isAuthInitializing } = useAuth();
  const userId = authUser?.user_id;

  const [insuranceData, setInsuranceData] = useState(initialInsuranceData);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const handleBack = () => navigate("/profile");

  const validateData = () => {
    const { insured, vehicle } = insuranceData;
    if (!insured.firstName || !insured.lastName || !insured.idNumber) {
      setError("กรุณากรอกข้อมูลผู้เอาประกันให้ครบถ้วน");
      return false;
    }
    if (!vehicle.licenseNo || !vehicle.make || !vehicle.model) {
      setError("กรุณากรอกข้อมูลรถยนต์ให้ครบถ้วน");
      return false;
    }
    return true;
  };

  const handleSave = async () => {
    if (!validateData() || saving) return;
    setSaving(true);

    try {
      const response = await saveInsuranceInfo(insuranceData);
      console.log("✅ บันทึกข้อมูลสำเร็จ:", response);
      alert("ข้อมูลถูกบันทึกแล้ว");
      navigate("/profile");
    } catch (err) {
      console.error("❌ ไม่สามารถบันทึกข้อมูลได้:", err);
      setError("ไม่สามารถบันทึกข้อมูลได้ กรุณาลองใหม่อีกครั้ง");
    } finally {
      setSaving(false);
    }
  };

  const loadUserProfile = useCallback(async () => {
    if (!userId || isAuthInitializing) return;

    try {
      const profile = await fetchUserProfile(userId);
      if (!profile?.customer) {
        navigate("/not-found");
        return;
      }

      const customer = profile.customer;
      const car = profile.car_info?.[0] || {};

      setInsuranceData((prev) => ({
        ...prev,
        insured: {
          ...prev.insured,
          firstName: customer.first_name || "",
          lastName: customer.last_name || "",
          idNumber: customer.id_card || "",
        },
        vehicle: {
          ...prev.vehicle,
          make: car.car_brand || "",
          model: car.car_model || "",
          modelYear: car.car_year || "",
        },
      }));
    } catch (err) {
      console.error("❌ โหลดข้อมูลล้มเหลว:", err);
      setError("ไม่สามารถโหลดข้อมูลโปรไฟล์ได้");
    } finally {
      setLoading(false);
    }
  }, [userId, isAuthInitializing, navigate]);

  useEffect(() => {
    if (!isAuthInitializing) loadUserProfile();
  }, [loadUserProfile, isAuthInitializing]);

  if (isAuthInitializing || loading) {
    return <div className="loading-message">⏳ กำลังโหลดข้อมูล...</div>;
  }

  return (
    <div className="prepare-insurance-page">
      <h1>เตรียมข้อมูลสำหรับประกันภัย</h1>

      {error && <div className="error-box">❌ {error}</div>}

      <InsuranceForm
        insuranceData={insuranceData}
        setInsuranceData={setInsuranceData}
        onSave={handleSave}
      />

      <div className="actions">
        <button className="back-btn" onClick={handleBack} disabled={saving}>
          ย้อนกลับ
        </button>
      </div>
    </div>
  );
};

export default PrepareInsuranceInfo;
