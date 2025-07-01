// /Users/apichet/Downloads/cheetah-insurance-app/src/pages/Login.jsx
// /Users/apichet/Downloads/cheetah-insurance-app/src/pages/Login.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login, requestPasswordReset } from "../api/authService";
import { useAuth } from "../context/AuthContext";
import "../assets/styles/Login.css";

const Login = () => {
  const navigate = useNavigate();
  const { loginUser } = useAuth(); // ✅ แก้ไขให้ตรงกับ AuthContext
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [showResetForm, setShowResetForm] = useState(false);
  const [resetEmail, setResetEmail] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (loading) return;
    setError("");
    setMessage("");
    setLoading(true);

    try {
      if (showResetForm) {
        console.log("🔄 [Login] Sending password reset request for:", resetEmail);
        await requestPasswordReset(resetEmail);
        setMessage("✅ Password reset link sent to your email.");
      } else {
        console.log("🔑 [Login] Attempting to login with:", formData.email);
        const response = await login(formData.email, formData.password);
        console.log("✅ [Login] Response received:", response);

        if (!response || !response.access_token || !response.refresh_token || !response.role) {
          throw new Error("Invalid login response from server.");
        }

        const { access_token, refresh_token, role } = response;
        loginUser(access_token, refresh_token, role); // ✅ เรียกใช้งาน loginUser จาก context
        console.log("🚀 [Login] Logged in successfully!");

        // ✅ บันทึก Token ตรวจสอบ localStorage
        console.log("📝 Auth Token:", localStorage.getItem("authToken"));
        console.log("📝 Refresh Token:", localStorage.getItem("refreshToken"));

        // ✅ นำทางตาม role ของผู้ใช้
        navigate(role === "admin" ? "/admin/dashboard" : "/profile");
      }
    } catch (err) {
      console.error("❌ [Login] Login failed:", err);
      setError(err.response?.data?.error || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      {/* ✅ ปุ่มกลับไปหน้าแรก */}
      <button className="back-home-btn" onClick={() => navigate("/")}>
        ⬅ Back to Home
      </button>

      <div className="container">
        <div className="form-panel">
          <h2>{showResetForm ? "Reset Password" : "Login"}</h2>
          {error && <p className="error-message">❌ {error}</p>}
          {message && <p className="success-message">✅ {message}</p>}

          <form onSubmit={handleSubmit}>
            {showResetForm ? (
              <>
                <div className="input-box">
                  <input
                    type="email"
                    name="resetEmail"
                    placeholder="Enter your email"
                    value={resetEmail}
                    onChange={(e) => setResetEmail(e.target.value)}
                    required
                  />
                  <i className="bx bxs-envelope"></i>
                </div>
                <button type="submit" className="btn" disabled={loading}>
                  {loading ? "Sending..." : "Send Reset Link"}
                </button>
                <button
                  type="button"
                  className="forgot-password"
                  onClick={() => setShowResetForm(false)}
                >
                  Back to Login
                </button>
              </>
            ) : (
              <>
                <div className="input-box">
                  <input
                    type="email"
                    name="email"
                    placeholder="Email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                  />
                  <i className="bx bxs-user"></i>
                </div>
                <div className="input-box">
                  <input
                    type="password"
                    name="password"
                    placeholder="Password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                  />
                  <i className="bx bxs-lock-alt"></i>
                </div>
                <button type="submit" className="btn" disabled={loading}>
                  {loading ? "Logging in..." : "Login"}
                </button>
              </>
            )}
          </form>

          {!showResetForm && (
            <button
              type="button"
              className="forgot-password"
              onClick={() => setShowResetForm(true)}
            >
              Forgot Password?
            </button>
          )}
        </div>

        <div className="toggle-box">
          <h1>Welcome Back</h1>
          <p>Don't have an account?</p>
          <button
            className="btn toggle-btn"
            onClick={() => navigate("/register")}
          >
            Register
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login;
