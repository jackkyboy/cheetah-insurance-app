// /Users/apichet/Downloads/cheetah-insurance-app/src/pages/AdminProfile.jsx
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useAuth } from "../context/AuthContext";

const AdminProfile = () => {
  const { authToken, logout } = useAuth();
  const navigate = useNavigate();
  const [adminData, setAdminData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchAdminProfile = async () => {
      try {
        console.log("🔍 Fetching Admin Profile...");
        
        const response = await axios.get("http://127.0.0.1:5000/api/admins/me", {
          headers: { Authorization: `Bearer ${authToken}` },
        });

        console.log("✅ Admin profile loaded:", response.data);
        setAdminData(response.data);
      } catch (err) {
        console.error("❌ Failed to load admin profile:", err);
        
        if (err.response?.status === 401) {
          console.warn("🚫 Unauthorized! Redirecting to login...");
          logout();
        } else {
          setError("Failed to load admin profile.");
        }
      }
    };

    if (authToken) fetchAdminProfile();
  }, [authToken]);

  if (error) return <p className="error-message">❌ {error}</p>;
  if (!adminData) return <p>⌛ Loading admin profile...</p>;

  return (
    <div className="admin-profile">
      <h2>Admin Profile</h2>
      <p><strong>Name:</strong> {adminData.name || "N/A"}</p>
      <p><strong>Email:</strong> {adminData.email}</p>
      <p><strong>Role:</strong> {adminData.role}</p>

      {/* ✅ ปุ่มไป Dashboard */}
      <button 
        className="dashboard-button"
        onClick={() => navigate("/admin/dashboard")}
      >
        Go to Dashboard
      </button>

      {/* ✅ ปุ่ม Logout */}
      <button 
        className="logout-button"
        onClick={logout}
      >
        Logout
      </button>
    </div>
  );
};

export default AdminProfile;
