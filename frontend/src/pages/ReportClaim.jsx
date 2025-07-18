import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext"; // Import AuthContext
import "../assets/styles/ReportClaim.css"; // Add CSS for styling

const insuranceCompanies = [
  { code: "MSIG", name_th: "บริษัท เอ็ม เอส ไอ จี ประกันภัย (ประเทศไทย) จำกัด (มหาชน)" },
  { code: "KPI", name_th: "บริษัท กรุงไทยพานิชประกันภัย จำกัด (มหาชน)" },
  { code: "Dhipaya", name_th: "บริษัท ทิพยประกันภัย จำกัด (มหาชน)" },
  { code: "AXA", name_th: "บริษัท แอกซ่าประกันภัย จำกัด (มหาชน)" },
  { code: "BKI", name_th: "บริษัท กรุงเทพประกันภัย จำกัด (มหาชน)" },
  { code: "Viriyah", name_th: "บริษัท วิริยะประกันภัย จำกัด (มหาชน)" },
  { code: "Falcon", name_th: "บริษัท ฟอลคอนประกันภัย จำกัด (มหาชน)" },
  { code: "Tokio Marine", name_th: "บริษัท คุ้มภัยโตเกียวมารีนประกันภัย (ประเทศไทย) จำกัด (มหาชน)" },
  { code: "Chubb", name_th: "บริษัท ชับบ์สามัคคีประกันภัย จำกัด (มหาชน)" },
  { code: "MTI", name_th: "บริษัท เมืองไทยประกันภัย จำกัด (มหาชน)" },
];

const ReportClaim = () => {
  const { authToken } = useAuth(); // Get authToken from AuthContext
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    policy_number: "",
    description: "",
    company_code: "",
    documents: [],
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  // Handle form field changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    setError("");
    setSuccess("");
  };

  // Handle file uploads
  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    setFormData({ ...formData, documents: files });
  };

  // Submit form data
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Ensure the user is authenticated
    if (!authToken) {
      setError("กรุณาเข้าสู่ระบบก่อนส่งข้อมูล");
      return;
    }

    // Validate required fields
    if (!formData.description.trim()) {
      setError("กรุณากรอกรายละเอียดปัญหา");
      return;
    }

    setLoading(true);
    try {
      const formPayload = new FormData();
      if (formData.policy_number.trim()) {
        formPayload.append("policy_number", formData.policy_number); // Include only if provided
      }
      formPayload.append("description", formData.description);
      formPayload.append("company_code", formData.company_code);
      formData.documents.forEach((file) => formPayload.append("documents", file));

      const response = await fetch("http://127.0.0.1:5000/api/claims", {
        method: "POST",
        body: formPayload,
        headers: {
          Authorization: `Bearer ${authToken}`, // Correct token usage
        },
        credentials: "include", // Include cookies/auth headers
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to submit claim.");
      }

      const result = await response.json();
      setSuccess("ส่งปัญหาเรียบร้อยแล้ว");
      setTimeout(() => navigate("/profile"), 1500);
    } catch (err) {
      console.error("❌ Error submitting claim report:", err.message);
      setError(err.message || "ไม่สามารถส่งข้อมูลได้ กรุณาลองอีกครั้ง");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="report-claim-page">
      <h2>แจ้งปัญหาเคลมประกันภัย</h2>
      {success && <div className="success-message">{success}</div>}
      {error && <div className="error-message">❌ {error}</div>}
      <form onSubmit={handleSubmit} className="report-claim-form">
        <div className="form-group">
          <label htmlFor="policy_number">เลขกรมธรรม์ (ถ้ามี):</label>
          <input
            type="text"
            id="policy_number"
            name="policy_number"
            placeholder="กรอกเลขกรมธรรม์ (ถ้ามี)"
            value={formData.policy_number}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label htmlFor="company_code">บริษัทประกันภัย:</label>
          <select
            id="company_code"
            name="company_code"
            value={formData.company_code}
            onChange={handleChange}
          >
            <option value="">เลือกบริษัทประกันภัย</option>
            {insuranceCompanies.map((company) => (
              <option key={company.code} value={company.code}>
                {company.name_th}
              </option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="description">รายละเอียดปัญหา:</label>
          <textarea
            id="description"
            name="description"
            placeholder="กรอกรายละเอียดปัญหา"
            value={formData.description}
            onChange={handleChange}
            required
          ></textarea>
        </div>
        <div className="form-group">
          <label htmlFor="documents">แนบเอกสาร (ถ้ามี):</label>
          <input
            type="file"
            id="documents"
            name="documents"
            multiple
            onChange={handleFileUpload}
          />
        </div>
        <div className="form-buttons">
          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? "⏳ กำลังส่ง..." : "ส่งปัญหา"}
          </button>
          <button type="button" className="cancel-btn" onClick={() => navigate("/profile")}>
            ยกเลิก
          </button>
        </div>
      </form>
    </div>
  );
};

export default ReportClaim;
