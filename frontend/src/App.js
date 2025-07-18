/*/Users/apichet/Downloads/cheetah-insurance-app/src/App.js*/
import React, { useEffect, useRef } from "react";
import { HashRouter, Routes, Route, useNavigate } from "react-router-dom";
import { applyTheme, getSavedTheme } from "./utils/themeToggle";
import "./assets/styles/theme.css"; // ✅ สำหรับ dark-theme
import { SearchProvider } from "./context/SearchContext";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { LoaderProvider, useLoader } from "./context/GlobalLoaderContext";
import ErrorBoundary from "./components/ErrorBoundary";
import Loader from "./components/LoaderComponent";
import ForgotPassword from "./pages/ForgotPassword";
import UploadedDocumentsPage from "./pages/UploadedDocumentsPage";


// Public Pages
import CompanyHome from "./pages/CompanyHome";
import Home from "./pages/Home";
import AdminLogin from "./pages/AdminLogin";
import Login from "./pages/Login";
import Register from "./pages/Register";
import PolicyMockupForm from "./pages/PolicyMockupForm";
import OCRDocument from "./pages/OCRDocument";
import CarBrandsPage from "./pages/CarBrandsPage";
import Chatbot from "./components/Chatbot";
import ChatAgent from './components/ChatAgent';
import "./assets/styles/chatbot.css";
import "./assets/styles/chatagent.css";


// Private Pages (User)
import Profile from "./pages/Profile";
import EditProfile from "./pages/EditProfile";
import PackageList from "./components/PackageList";
import MultiStepSearch from "./components/MultiStepSearch";
import PackageDetail from "./components/PackageDetails";
import PrepareInsuranceInfo from "./pages/PrepareInsuranceInfo";
import PolicyDocument from "./pages/PolicyDocument";
import ReportClaim from "./pages/ReportClaim";
import ReviewInsurance from "./pages/ReviewInsurance";
import SearchResults from "./components/SearchResults";
import OrderStatus from "./components/OrderStatus";

// Private Pages (Admin)
import AdminDashboard from "./pages/AdminDashboard";
import AdminProfile from "./pages/AdminProfile";

// Route Guards
import PrivateRoute from "./components/PrivateRoute";
import AdminRoute from "./components/AdminRoute";

import PackageGallery from "./components/PackageGallery"; // หรือ "./pages/PackageGallery" ถ้าแยกหน้า

// ✅ 404 Page Component แยกไว้ด้านบน
const NotFound = () => (
  <div style={{ textAlign: "center", padding: "50px" }}>
    <h1>404 - Page Not Found</h1>
    <p>ขออภัย หน้าที่คุณกำลังมองหาไม่มีอยู่ในระบบ</p>
    <a href="/" style={{ textDecoration: "none", color: "blue" }}>
      กลับไปหน้าแรก
    </a>
  </div>
);

// ✅ Public routes (ไม่ต้องมี token)
const PUBLIC_PATHS = ["/", "/home", "/login", "/register", "/forgot-password", "/admin/login"];

const AppContent = () => {
  const { isLoading } = useLoader();
  const { isAuthInitializing, authToken } = useAuth();
  const navigate = useNavigate();
  const hasRedirected = useRef(false);

  // ✅ Load theme once on mount
  useEffect(() => {
    const saved = getSavedTheme();
    applyTheme(saved);
  }, []);

  // ✅ Redirect to login if needed
  useEffect(() => {
    const shouldRedirect = () =>
      !isAuthInitializing &&
      !authToken &&
      !hasRedirected.current &&
      !PUBLIC_PATHS.some((path) => window.location.pathname.startsWith(path));

    if (shouldRedirect()) {
      hasRedirected.current = true;
      navigate("/login", { replace: true });
    }
  }, [isAuthInitializing, authToken, navigate]);

  // ✅ Show loading
  if (isAuthInitializing || isLoading) {
    return <p style={{ textAlign: "center", padding: "50px" }}>🔄 กำลังโหลดข้อมูล...</p>;
  }

  // ✅ Main routes
  return (
    <>
      {isLoading && <Loader />}
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<CompanyHome />} />
        <Route path="/home" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route path="/car-brands" element={<CarBrandsPage />} />
        <Route path="/mockup-policy" element={<PolicyMockupForm />} />
        <Route path="/ocr" element={<OCRDocument />} />
        <Route path="/chat-agent" element={<ChatAgent />} />
        <Route path="/gallery" element={<PackageGallery />} />

        {/* Private Routes (User) */}
        <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
        <Route path="/edit-profile" element={<PrivateRoute><EditProfile /></PrivateRoute>} />
        <Route path="/packages" element={<PrivateRoute><PackageList /></PrivateRoute>} />
        <Route path="/compare" element={<PrivateRoute><MultiStepSearch /></PrivateRoute>} />
        <Route path="/package/:id" element={<PrivateRoute><PackageDetail /></PrivateRoute>} />
        <Route path="/prepare-insurance-info" element={<PrivateRoute><PrepareInsuranceInfo /></PrivateRoute>} />
        <Route path="/policy-document" element={<PrivateRoute><PolicyDocument /></PrivateRoute>} />
        <Route path="/report-claim" element={<PrivateRoute><ReportClaim /></PrivateRoute>} />
        <Route path="/review-insurance" element={<PrivateRoute><ReviewInsurance /></PrivateRoute>} />
        <Route path="/search-results" element={<PrivateRoute><SearchResults /></PrivateRoute>} />
        <Route path="/order/:orderId" element={<PrivateRoute><OrderStatus /></PrivateRoute>} />
        <Route path="/uploaded-documents" element={<PrivateRoute><UploadedDocumentsPage /></PrivateRoute>} />

        {/* Private Routes (Admin) */}
        <Route path="/admin/dashboard" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
        <Route path="/admin/profile" element={<AdminRoute><AdminProfile /></AdminRoute>} />

        {/* 404 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
      <Chatbot floating />
    </>
  );
};

// ✅ Main App (ควบคุม Context และ Routing)
const App = () => {
  return (
    <AuthProvider>
      <LoaderProvider>
        <ErrorBoundary>
          <SearchProvider>
            <AppContent />
          </SearchProvider>
        </ErrorBoundary>
      </LoaderProvider>
    </AuthProvider>
  );
};

export default App;
