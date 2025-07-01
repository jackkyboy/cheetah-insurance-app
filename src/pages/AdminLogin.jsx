// /Users/apichet/Downloads/cheetah-insurance-app/src/pages/AdminLogin.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { adminLogin } from "../api/adminAuthService"; 
import { useAuth } from "../context/AuthContext";

const AdminLogin = () => {
  const navigate = useNavigate();
  const { login: setAuth } = useAuth();
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
  
    try {
      console.log("🔍 Attempting Admin Login...");
  
      const response = await adminLogin(formData.email, formData.password);
      console.log("🔄 API Response:", response);
  
      if (!response || !response.access_token || !response.refresh_token || !response.role) {
        throw new Error("Invalid login response. Missing tokens or role.");
      }
  
      const { access_token, refresh_token, role } = response;
      console.log("✅ Login Successful. Role:", role);
  
      // ✅ Save Tokens and Role
      localStorage.setItem("authToken", access_token);
      localStorage.setItem("refreshToken", refresh_token);
      localStorage.setItem("role", role);

      // ✅ Set Authentication Context
      setAuth(access_token, refresh_token, role);
      console.log("🔓 Auth State Updated!");

      // ✅ Redirect ไปยัง ProfileAdmin ก่อน
      console.log("🔀 Redirecting to /admin/profile...");
      navigate("/admin/profile");
    } catch (err) {
      console.error("❌ Admin Login Failed:", err.message);
      setError(err.response?.data?.error || err.message || "An error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <h2>Admin Login</h2>
        {error && <p className="error-message">❌ {error}</p>}
        <form onSubmit={handleSubmit}>
          <input
            type="email"
            name="email"
            placeholder="Admin Email"
            value={formData.email}
            onChange={handleChange}
            required
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AdminLogin;
