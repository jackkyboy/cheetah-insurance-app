// /Users/apichet/Downloads/cheetah-insurance-app/src/pages/Register.jsx
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
    car_brand: "",
    car_model: "",
    car_year: "",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError("");
    setSuccess("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.car_brand || !formData.car_model || !formData.car_year) {
      setError("กรุณากรอกข้อมูลรถยนต์ให้ครบถ้วน");
      return;
    }
    if (formData.password !== formData.confirmPassword) {
      setError("รหัสผ่านไม่ตรงกัน");
      return;
    }
    try {
      const result = await register({
        email: formData.email,
        password: formData.password,
        car_brand: formData.car_brand,
        car_model: formData.car_model,
        car_year: formData.car_year,
      });
      setSuccess("สมัครสมาชิกสำเร็จ!");
      console.log("Registration successful:", result);
      navigate("/login");
    } catch (err) {
      setError(err.message || "เกิดข้อผิดพลาดในการสมัครสมาชิก");
      console.error("Registration failed:", err);
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
          <button type="button" className="back-login-btn" onClick={() => navigate("/login")}>
            กลับไปหน้า Login
          </button>
        </form>
      </div>
    </div>
  );
};

export default Register;
