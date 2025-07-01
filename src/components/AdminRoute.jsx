// /Users/apichet/Downloads/cheetah-insurance-app/src/components/AdminRoute.jsx
import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const AdminRoute = ({ children }) => {
  const { user, authToken, role, isAuthInitializing, isAdmin } = useAuth();
  const location = useLocation();

  console.log("🔍 [AdminRoute] Checking Admin Access:", { user, authToken, role, isAuthInitializing, isAdmin });

  // ⏳ ถ้า AuthContext กำลังโหลดข้อมูลอยู่ รออย่าเพิ่ง Redirect
  if (isAuthInitializing) {
    console.warn("⏳ [AdminRoute] Authentication is initializing... Waiting.");
    return (
      <div style={{ textAlign: "center", marginTop: "20%" }}>
        <h2>Loading...</h2>
        <p>Please wait...</p>
      </div>
    );
  }

  // ❌ ถ้าไม่มี Token หรือ Token ใช้ไม่ได้ ให้ Redirect ไปที่ Login
  if (!authToken) {
    console.error("❌ [AdminRoute] Unauthorized! Redirecting to /admin/login");
    return <Navigate to="/admin/login" state={{ from: location }} replace />;
  }

  // ✅ ตรวจสอบสิทธิ์ Admin อย่างถูกต้อง
  if (role !== "admin" || !isAdmin) {
    console.warn("🚫 [AdminRoute] User is not an admin. Redirecting to /");
    return <Navigate to="/" replace />;
  }

  // ✅ ถ้าทุกอย่างโอเค ให้ Render หน้า Admin
  console.log("✅ [AdminRoute] Access Granted! Rendering Admin Page.");
  return children;
};

export default AdminRoute;
