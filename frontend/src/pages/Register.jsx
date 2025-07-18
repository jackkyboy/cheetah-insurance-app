// /Users/apichet/Downloads/cheetah-insurance-app/src/pages/Register.jsx
// /src/pages/Register.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { register } from "../api/authService";
import "../assets/styles/Register.css";

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    first_name: "",
    last_name: "",
    car_brand: "",
    car_model: "",
    car_year: "",
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError("");
    setSuccess("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // 🚫 Basic validations
    const {
      email,
      password,
      confirmPassword,
      first_name,
      last_name,
      car_brand,
      car_model,
      car_year,
    } = formData;

    if (!email || !password || !confirmPassword || !first_name || !last_name) {
      setError("กรุณากรอกข้อมูลให้ครบถ้วน");
      return;
    }

    if (!car_brand || !car_model || !car_year) {
      setError("กรุณากรอกข้อมูลรถยนต์ให้ครบถ้วน");
      return;
    }

    if (password !== confirmPassword) {
      setError("รหัสผ่านไม่ตรงกัน");
      return;
    }

    try {
      const result = await register({
        email,
        password,
        first_name,
        last_name,
        car_brand,
        car_model,
        car_year,
      });

      setSuccess("สมัครสมาชิกสำเร็จ!");
      console.log("✅ Registration successful:", result);
      setTimeout(() => navigate("/login"), 1000);
    } catch (err) {
      console.error("❌ Registration failed:", err);
      setError(err.response?.data?.error || "เกิดข้อผิดพลาดในการสมัครสมาชิก");
    }
  };

  return (
    <div className="register-page">
      <div className="register-container">
        <form className="register-form" onSubmit={handleSubmit}>
          <h2>สมัครสมาชิก</h2>
          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}

          <div className="register-input">
            <input
              type="email"
              name="email"
              placeholder="อีเมล"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="register-input">
            <input
              type="text"
              name="first_name"
              placeholder="ชื่อจริง"
              value={formData.first_name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="register-input">
            <input
              type="text"
              name="last_name"
              placeholder="นามสกุล"
              value={formData.last_name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="register-input">
            <input
              type="password"
              name="password"
              placeholder="รหัสผ่าน"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>

          <div className="register-input">
            <input
              type="password"
              name="confirmPassword"
              placeholder="ยืนยันรหัสผ่าน"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
            />
          </div>

          <div className="register-input">
            <input
              type="text"
              name="car_brand"
              placeholder="ยี่ห้อรถยนต์"
              value={formData.car_brand}
              onChange={handleChange}
              required
            />
          </div>

          <div className="register-input">
            <input
              type="text"
              name="car_model"
              placeholder="รุ่นรถยนต์"
              value={formData.car_model}
              onChange={handleChange}
              required
            />
          </div>

          <div className="register-input">
            <input
              type="text"
              name="car_year"
              placeholder="ปีรถยนต์"
              value={formData.car_year}
              onChange={handleChange}
              required
            />
          </div>

          <button type="submit" className="register-btn">สมัครสมาชิก</button>
          <button
            type="button"
            className="back-login-btn"
            onClick={() => navigate("/login")}
          >
            กลับไปหน้า Login
          </button>
        </form>
      </div>
    </div>
  );
};

export default Register;
