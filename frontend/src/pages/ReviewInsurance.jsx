/*/Users/apichet/Downloads/cheetah-insurance-app/src/pages/ReviewInsurance.jsx */
import React, { useState } from "react";
import "../assets/styles/ReviewInsurance.css"; // Specific styling
import "../assets/styles/SatisfactionSlider.css"; // 👉 อย่าลืมสร้างไฟล์ CSS ตามด้านล่าง
import { submitReview } from "../api/reviewService"; // API service for review submission
import { useNavigate } from "react-router-dom";

// List of insurance companies
const insuranceCompanies = [
  { id: 1, name: "บริษัท เอ็ม เอส ไอ จี ประกันภัย (ประเทศไทย) จำกัด (มหาชน)" },
  { id: 2, name: "บริษัท กรุงไทยพานิชประกันภัย จำกัด (มหาชน)" },
  { id: 3, name: "บริษัท ทิพยประกันภัย จำกัด (มหาชน)" },
  { id: 4, name: "บริษัท แอกซ่าประกันภัย จำกัด (มหาชน)" },
  { id: 5, name: "บริษัท กรุงเทพประกันภัย จำกัด (มหาชน)" },
  { id: 6, name: "บริษัท วิริยะประกันภัย จำกัด (มหาชน)" },
  { id: 7, name: "บริษัท ฟอลคอนประกันภัย จำกัด (มหาชน)" },
  { id: 8, name: "บริษัท คุ้มภัยโตเกียวมารีนประกันภัย (ประเทศไทย) จำกัด (มหาชน)" },
  { id: 9, name: "บริษัท ชับบ์สามัคคีประกันภัย จำกัด (มหาชน)" },
  { id: 10, name: "บริษัท เมืองไทยประกันภัย จำกัด (มหาชน)" },
];
const ReviewInsurance = () => {
  const [formState, setFormState] = useState({
    packageId: "",
    rating: 0,
    comment: "",
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (field) => (e) => {
    const value = field === "rating" ? Number(e.target.value) : e.target.value;
    setFormState((prev) => ({ ...prev, [field]: value }));
    setError("");
  };

  const validateForm = () => {
    const { packageId, rating, comment } = formState;

    if (!packageId) return "กรุณาเลือกบริษัทประกันภัย";
    if (rating === 0 || comment.trim() === "") return "กรุณาให้คะแนนและแสดงความคิดเห็น";
    if (comment.length > 500) return "ความคิดเห็นต้องไม่เกิน 500 ตัวอักษร";
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    try {
      const reviewData = {
        company_id: formState.packageId, // ✅ เพิ่มเข้าไปตามที่ backend ต้องการ
        package_id: formState.packageId,
        rating: formState.rating,
        comment: formState.comment.trim(),
      };
      

      console.log("📦 Review payload:", reviewData);
      await submitReview(reviewData);

      setSuccess("ขอบคุณสำหรับการรีวิว!");
      setTimeout(() => navigate("/profile"), 2000);
    } catch (err) {
      const errorMessage =
        err?.response?.data?.error || err?.error || "เกิดข้อผิดพลาดในการส่งรีวิว กรุณาลองอีกครั้ง";
      console.error("[ReviewInsurance] Review submission failed:", err);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="review-insurance-page">
      <h2>รีวิวประกันภัย</h2>
  
      {error && <div className="error-message">❌ {error}</div>}
      {success && <div className="success-message">✅ {success}</div>}
  
      <form onSubmit={handleSubmit} className="review-form">
        <div className="form-group">
          <label htmlFor="insurance-package">บริษัทประกันภัย:</label>
          <select
            id="insurance-package"
            value={formState.packageId}
            onChange={handleChange("packageId")}
            className="company-dropdown"
            disabled={loading}
          >
            <option value="">เลือกบริษัทประกันภัย</option>
            {insuranceCompanies.map((company) => (
              <option key={company.id} value={company.id}>
                {company.name}
              </option>
            ))}
          </select>
        </div>
  
        <div className="rating-section">
          <label htmlFor="satisfaction">😊 ระดับความพึงพอใจ:</label>
          <input
            type="range"
            id="satisfaction"
            name="satisfaction"
            className="satisfaction"
            min="1"
            max="5"
            step="1"
            value={formState.rating}
            onChange={handleChange("rating")}
            style={{ '--val': formState.rating }}
            aria-valuemin={1}
            aria-valuemax={5}
            aria-valuenow={formState.rating}
            aria-label={`ระดับความพึงพอใจ: ${formState.rating} ดาว`}
            disabled={loading}
          />
        </div>
  
        <textarea
          placeholder="เขียนความคิดเห็นของคุณ..."
          value={formState.comment}
          onChange={handleChange("comment")}
          rows="5"
          className="review-textarea"
          maxLength="500"
          disabled={loading}
        />
  
        <div className="form-buttons">
          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? "⏳ กำลังส่ง..." : "ส่งรีวิว"}
          </button>
          <button
            type="button"
            className="cancel-btn"
            onClick={() => navigate("/profile")}
            disabled={loading}
          >
            ยกเลิก
          </button>
        </div>
      </form>
    </div>
  );
  
  
  
};

export default ReviewInsurance;
