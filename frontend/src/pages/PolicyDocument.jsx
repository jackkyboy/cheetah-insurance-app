// /Users/apichet/Downloads/cheetah-insurance-app/src/pages/PolicyDocument.jsx
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../assets/styles/PolicyDocument.css";
import { getInsurancePreparation } from "../api/insuranceService";
import { jwtDecode } from "jwt-decode"; // Corrected import

const PolicyDocument = () => {
  const [insuranceData, setInsuranceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchInsuranceData = async () => {
      try {
        const token = localStorage.getItem("authToken");

        if (!token) {
          setError("กรุณาเข้าสู่ระบบ");
          navigate("/login");
          return;
        }

        // Decode the JWT token to get the user_id
        const decoded = jwtDecode(token);
        const userId = decoded?.user_id;

        if (!userId) {
          throw new Error("ไม่พบข้อมูลผู้ใช้งานในโทเค็น");
        }

        console.log("🔍 Fetching insurance preparation for user_id:", userId);
        const response = await getInsurancePreparation(userId);

        if (!response || !response.data) {
          throw new Error("ไม่พบข้อมูลกรมธรรม์สำหรับผู้ใช้งานนี้");
        }

        setInsuranceData(response.data);
        console.log("✅ Insurance preparation fetched successfully:", response.data);
      } catch (err) {
        console.error("❌ Error fetching insurance preparation:", err.message);
        setError(err.message || "เกิดข้อผิดพลาดในการดึงข้อมูลกรมธรรม์");
      } finally {
        setLoading(false);
      }
    };

    fetchInsuranceData();
  }, [navigate]);

  // Helper function to render field values
  const renderField = (label, value) => (
    <p>
      <strong>{label}:</strong> {value || "ไม่ระบุ"}
    </p>
  );

  if (loading) {
    return <div className="loading-message">⏳ กำลังโหลดข้อมูล...</div>;
  }

  if (error) {
    return (
      <div className="error-message">
        ❌ {error}
        <div className="button-group">
          <button className="btn back-btn" onClick={() => navigate("/")}>
            ย้อนกลับไปหน้าแรก
          </button>
          <button className="btn retry-btn" onClick={() => window.location.reload()}>
            ลองอีกครั้ง
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="policy-document">
      <h1 className="document-title">เอกสารกรมธรรม์</h1>

      {/* Section: ข้อมูลผู้เอาประกัน */}
      <section className="section">
        <h2>ข้อมูลผู้เอาประกัน</h2>
        {renderField("คำนำหน้า", insuranceData?.insured_info?.title)}
        {renderField(
          "ชื่อ",
          `${insuranceData?.insured_info?.first_name || ""} ${insuranceData?.insured_info?.last_name || ""}`.trim()
        )}
        {renderField("หมายเลขบัตรประชาชน", insuranceData?.insured_info?.id_card)}
        {renderField("อีเมล", insuranceData?.insured_info?.email)}
      </section>

      {/* Section: ข้อมูลรถยนต์ */}
      <section className="section">
        <h2>ข้อมูลรถยนต์</h2>
        {renderField("เลขทะเบียนรถ", insuranceData?.motor_info?.license_no)}
        {renderField("ยี่ห้อรถ", insuranceData?.motor_info?.make)}
        {renderField("รุ่นรถ", insuranceData?.motor_info?.model)}
        {renderField("ปี", insuranceData?.motor_info?.year)}
      </section>

      {/* Section: ข้อมูลกรมธรรม์ */}
      <section className="section">
        <h2>ข้อมูลกรมธรรม์</h2>
        {renderField("รหัสแพคเกจ", insuranceData?.policy_info?.package_code)}
        {renderField(
          "เบี้ยประกันภัยรวม",
          insuranceData?.policy_info?.total_premium
            ? insuranceData.policy_info.total_premium.toLocaleString("th-TH", {
                style: "currency",
                currency: "THB",
              })
            : "ไม่ระบุ"
        )}
      </section>

      {/* Buttons */}
      <div className="button-group">
        <button className="btn back-btn" onClick={() => navigate("/")}>
          ย้อนกลับไปหน้าแรก
        </button>
        <button className="btn profile-btn" onClick={() => navigate("/profile")}>
          ไปยังหน้าโปรไฟล์
        </button>
      </div>
    </div>
  );
};

export default PolicyDocument;
