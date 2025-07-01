/*/Users/apichet/Downloads/cheetah-insurance-app/src/pages/EditProfile.jsx */
import React, { useState, useEffect } from "react";
import { fetchUserProfile, updateUserProfile } from "../api/userService";
import { useNavigate } from "react-router-dom";
import "../assets/styles/EditProfile.css";

const EditProfile = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    phone_number: "",
    car_brand: "",
    car_model: "",
    car_year: "",
    car_submodel: "",
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const data = await fetchUserProfile();
        if (!data || !data.customer) {
          throw new Error("ไม่พบข้อมูลผู้ใช้");
        }
        const carInfo = Array.isArray(data.car_info) && data.car_info[0] ? data.car_info[0] : {};
        setFormData({
          first_name: data.customer.first_name || "",
          last_name: data.customer.last_name || "",
          phone_number: data.customer.phone_number || "",
          car_brand: carInfo.car_brand || "",
          car_model: carInfo.car_model || "",
          car_year: carInfo.car_year || "",
          car_submodel: carInfo.car_submodel || "",
        });
        setLoading(false);
      } catch (err) {
        console.error("❌ Error loading profile:", err.message);
        setError("ไม่สามารถโหลดข้อมูลได้");
        setLoading(false);
      }
    };

    loadProfile();
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError("");
    setSuccess("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        first_name: formData.first_name.trim(),
        last_name: formData.last_name.trim(),
        phone_number: formData.phone_number.trim(),
        car_info: {
          car_brand: formData.car_brand.trim(),
          car_model: formData.car_model.trim(),
          car_year: formData.car_year.trim(),
          car_submodel: formData.car_submodel.trim(),
        },
      };

      // Validate required fields
      if (!payload.first_name || !payload.last_name || !payload.phone_number) {
        setError("กรุณากรอกข้อมูลที่จำเป็นให้ครบถ้วน");
        return;
      }

      await updateUserProfile(payload);
      setSuccess("อัปเดตข้อมูลสำเร็จ!");
      setTimeout(() => navigate("/profile", { replace: true, state: { reload: true } }), 1500);
    } catch (err) {
      console.error("❌ Error updating profile:", err.message);
      setError("ไม่สามารถอัปเดตข้อมูลได้ กรุณาลองอีกครั้ง");
    }
  };

  const handleReset = () => {
    setFormData({
      first_name: "",
      last_name: "",
      phone_number: "",
      car_brand: "",
      car_model: "",
      car_year: "",
      car_submodel: "",
    });
    setError("");
    setSuccess("");
  };

  if (loading) return <div className="loading-message">⏳ กำลังโหลดข้อมูล...</div>;
  if (error && !formData.first_name) return <div className="error-message">❌ {error}</div>;

  return (
    <div className="edit-profile-page">
      <h2>แก้ไขโปรไฟล์</h2>
      {success && <div className="success-message">{success}</div>}
      {error && <div className="error-message">{error}</div>}
      <form onSubmit={handleSubmit} className="edit-profile-form">
        <input
          type="text"
          name="first_name"
          placeholder="ชื่อ"
          value={formData.first_name}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="last_name"
          placeholder="นามสกุล"
          value={formData.last_name}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="phone_number"
          placeholder="เบอร์โทรศัพท์"
          value={formData.phone_number}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="car_brand"
          placeholder="ยี่ห้อรถยนต์"
          value={formData.car_brand}
          onChange={handleChange}
        />
        <input
          type="text"
          name="car_model"
          placeholder="รุ่นรถยนต์"
          value={formData.car_model}
          onChange={handleChange}
        />
        <input
          type="text"
          name="car_year"
          placeholder="ปีรถยนต์"
          value={formData.car_year}
          onChange={handleChange}
        />
        <input
          type="text"
          name="car_submodel"
          placeholder="รุ่นย่อย"
          value={formData.car_submodel}
          onChange={handleChange}
        />
        <div className="form-buttons">
          <button type="submit" className="save-btn">
            บันทึก
          </button>
          <button type="button" className="cancel-btn" onClick={() => navigate("/profile")}>
            ยกเลิก
          </button>
          <button type="button" className="reset-btn" onClick={handleReset}>
            ล้างข้อมูล
          </button>
        </div>
      </form>
    </div>
  );
};

export default EditProfile;
