/*/Users/apichet/Downloads/cheetah-insurance-app/src/components/PrivateRoute.jsx*/
import React, { useEffect, useState, useMemo } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { jwtDecode } from "jwt-decode";

const PrivateRoute = ({ children }) => {
  const authContext = useAuth();
  const {
    authToken,
    isAuthInitializing,
    user,
    isAdmin,
    handleTokenRefresh,
    isRefreshing, // ✅ เพิ่ม State เช็คว่ากำลัง Refresh Token อยู่หรือไม่
  } = authContext || {}; // ✅ ป้องกัน error ถ้า `useAuth()` คืนค่า `null`

  const location = useLocation();
  const [isLoading, setIsLoading] = useState(true);

  // ✅ ฟังก์ชันตรวจสอบว่า Token หมดอายุหรือไม่
  const isTokenExpired = (token) => {
    try {
      const decoded = jwtDecode(token);
      return decoded.exp * 1000 < Date.now();
    } catch (err) {
      console.error("❌ [isTokenExpired] Error decoding token:", err);
      return true;
    }
  };

  // ✅ ตรวจสอบว่าผู้ใช้ได้รับการยืนยันหรือยัง (รวมถึงรอ Refresh)
  const isAuthenticated = useMemo(() => {
    return (
      authToken &&
      (user?.user_id !== undefined || user?.admin_id !== undefined) &&
      (!isTokenExpired(authToken) || isRefreshing) // ✅ ป้องกัน Redirect ถ้า Token หมดอายุแต่กำลัง Refresh อยู่
    );
  }, [authToken, user, isRefreshing]);

  // ✅ ตรวจสอบการหมดอายุของ Token และเรียก Refresh
  useEffect(() => {
    const verifyAuth = async () => {
      console.log("🔍 [PrivateRoute] Checking authentication...");

      if (authToken && isTokenExpired(authToken) && handleTokenRefresh) {
        console.warn("⚠️ [PrivateRoute] Token expired. Refreshing...");
        await handleTokenRefresh();

        // ⏳ รอให้ Token ใหม่ถูกอัปเดตก่อน Render (รอ 500ms)
        await new Promise((resolve) => setTimeout(resolve, 500));

        console.log("✅ [PrivateRoute] Token refreshed:", authToken);
      }
      setIsLoading(false);
    };

    if (!isAuthInitializing) {
      verifyAuth();
    }
  }, [authToken, isAuthInitializing, handleTokenRefresh]);

  // 🔍 Debug Log เพื่อตรวจสอบค่าต่างๆ
  console.log("🔍 [PrivateRoute] Debug Info:", {
    authToken,
    isAuthInitializing,
    isAuthenticated,
    isTokenExpired: authToken ? isTokenExpired(authToken) : "No Token",
    isRefreshing,
  });

  // 🔄 Loading State
  if (isLoading || isAuthInitializing) {
    return (
      <div style={{ textAlign: "center", marginTop: "20%" }}>
        <h2>Loading...</h2>
        <p>Please wait...</p>
      </div>
    );
  }

  // ❌ Redirect ถ้ายังไม่ได้ Authenticated (ยกเว้นถ้ากำลัง Refresh)
  if (!isAuthenticated) {
    console.warn("❌ [PrivateRoute] User is not authenticated. Redirecting to /login...");
    return <Navigate to="/login" replace />;
  }

  // 🚫 Admin ไม่สามารถเข้า `/profile`
  if (isAdmin && location.pathname.startsWith("/profile")) {
    console.warn("❌ [PrivateRoute] Admin cannot access User Profile. Redirecting...");
    return <Navigate to="/admin/dashboard" replace />;
  }

  // 🚫 User ไม่สามารถเข้าถึงหน้า `/admin`
  if (!isAdmin && location.pathname.startsWith("/admin")) {
    console.warn("❌ [PrivateRoute] User cannot access Admin Dashboard. Redirecting...");
    return <Navigate to="/profile" replace />;
  }

  // ✅ Authenticated ผ่านแล้ว แสดง Children Components
  console.log("✅ [PrivateRoute] Authentication successful. Rendering children.");
  return children;
};

export default PrivateRoute;
