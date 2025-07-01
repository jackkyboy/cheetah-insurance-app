// /Users/apichet/Downloads/cheetah-insurance-app/src/pages/ForgotPassword.jsx

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import apiClient from "../api/authService";

const ForgotPassword = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setError("");
    setLoading(true);

    try {
      const response = await apiClient.post("/auth/forgot-password", { email });
      setMessage(response.data.message);
      console.log("📩 Reset password request sent:", response.data);
    } catch (err) {
      setError(err.response?.data?.error || "Failed to send reset password request.");
      console.error("❌ Error requesting password reset:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="forgot-password-container">
      <div className="forgot-password-card">
        <h2>Forgot Password</h2>
        <p>Enter your email to receive a password reset link.</p>
        {message && <p className="success-message">✅ {message}</p>}
        {error && <p className="error-message">❌ {error}</p>}
        <form onSubmit={handleSubmit}>
          <input
            type="email"
            name="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? "Sending..." : "Send Reset Link"}
          </button>
        </form>
        <button className="back-button" onClick={() => navigate("/login")}>
          Back to Login
        </button>
      </div>
    </div>
  );
};

export default ForgotPassword;
