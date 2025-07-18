// /Users/apichet/Downloads/cheetah-insurance-app/src/pages/Profile.jsx
import React, { useEffect, useState, useMemo } from "react";
import "../assets/styles/Profile.css";
import { useNavigate } from "react-router-dom";
import {
  fetchUserProfile,
  logoutUser,
  uploadProfilePicture,
} from "../api/userService";
import {
  fetchCustomerDocuments,
  uploadDocument,
  deleteDocument,
} from "../api/documentService";
import { fetchOrderHistory } from "../api/orderService";

import ProfilePicture from "../components/ProfilePicture";
import UserDetails from "../components/UserDetails";
import DocumentsSection from "../components/DocumentsSection";
import OrderHistorySection from "../components/OrderHistorySection";
import ProfileActions from "../components/ProfileActions";
import { REQUIRED_DOCUMENTS } from "../constants/documents";

const DEFAULT_PROFILE_PICTURE = "/images/default-profile.png?v=1";
const LOCAL_STORAGE_KEY = "profile_picture_url";



// Generic data fetcher
const fetchData = async (fetchFn, setData, setLoading, setError, fallbackMessage, fallbackData = null) => {
  setLoading?.(true);
  try {
    const data = await fetchFn();
    setData(data || fallbackData);
    setError("");
  } catch (err) {
    const message = err?.message || "Unknown error";
    if (message.includes("currently being fetched")) return;
    console.error(`❌ ${fallbackMessage}:`, message);
    setError(fallbackMessage);
    if (fallbackData) setData(fallbackData);
  } finally {
    setLoading?.(false);
  }
};

const Profile = () => {
  const [user, setUser] = useState(null);
  
  const [documents, setDocuments] = useState([]);
  const [orderHistory, setOrderHistory] = useState([]);

  const [errorProfile, setErrorProfile] = useState("");
  const [errorDocuments, setErrorDocuments] = useState("");
  const [errorOrders, setErrorOrders] = useState("");

  const [loadingProfile, setLoadingProfile] = useState(false);
  const [loadingDocuments, setLoadingDocuments] = useState(false);
  const [loadingOrders, setLoadingOrders] = useState(false);

  const [uploading, setUploading] = useState(false);
  const [profilePictureUploading, setProfilePictureUploading] = useState(false);

  const navigate = useNavigate();

  // ✅ Profile picture (will be auto-refreshed due to ?t=...)
  // ✅ Profile picture (will be auto-refreshed due to ?t=...)
  const profilePictureUrl = useMemo(() => {
    const stored = localStorage.getItem("profile_picture_url");
    const path = user?.customer?.profile_picture || stored;
  
    const base = process.env.REACT_APP_API_BASE_URL || window.location.origin;
  
    if (!path) return DEFAULT_PROFILE_PICTURE;
    if (path.startsWith("http")) return path;
    return `${base}${path}`;
  }, [user?.customer?.profile_picture]);
  

  
  

  useEffect(() => {
    fetchData(fetchUserProfile, setUser, setLoadingProfile, setErrorProfile, "ไม่สามารถโหลดข้อมูลโปรไฟล์ได้");
  }, []);

  useEffect(() => {
    const cid = user?.customer?.customer_id;
    if (!cid) return;

    fetchData(() => fetchCustomerDocuments(cid), setDocuments, setLoadingDocuments, setErrorDocuments, "ไม่สามารถโหลดข้อมูลเอกสารได้");
    fetchData(() => fetchOrderHistory(cid), setOrderHistory, setLoadingOrders, setErrorOrders, "ไม่สามารถโหลดข้อมูลคำสั่งซื้อได้");
  }, [user]);




  // ✅ Upload เอกสารแนบ (แบบ sync กับ backend)/Users/apichet/Downloads/cheetah-insurance-app/src/pages/Profile.jsx
  // ✅ Upload เอกสารแนบ (แบบ sync กับ backend)
  // ✅ Upload เอกสารแนบ (แบบ sync กับ backend)
  const handleUploadDocument = async (e, docType) => {
    const file = e.target.files?.[0];
    const customer_id = user?.customer?.customer_id;

    if (!file || !docType || !customer_id) {
      alert("ข้อมูลไม่ครบถ้วน ไม่สามารถอัปโหลดเอกสารได้");
      return;
    }

    setUploading(true);

    try {
      const response = await uploadDocument({
        customer_id,
        document_type: docType,
        file,
      });

      if (response?.document_id) {
        setDocuments((prev) => [...prev, response]);
        console.info("✅ อัปโหลดเอกสารสำเร็จ:", response);
      } else {
        console.warn("⚠️ อัปโหลดสำเร็จแต่ไม่ได้รับข้อมูลเอกสารกลับมา");
        alert("อัปโหลดสำเร็จ แต่ระบบไม่ได้ตอบกลับข้อมูลเอกสาร");
      }
    } catch (error) {
      console.error("❌ เกิดข้อผิดพลาดระหว่างการอัปโหลดเอกสาร:", error?.response?.data || error.message);
      alert("เกิดข้อผิดพลาดระหว่างการอัปโหลดเอกสาร กรุณาลองใหม่");
    } finally {
      setUploading(false);
    }
  };

  


  

  // ✅ ลบเอกสาร
  const handleDeleteDocument = async (id) => {
    if (!window.confirm("คุณแน่ใจหรือไม่ว่าต้องการลบเอกสารนี้?")) return;
    try {
      await deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.document_id !== id));
    } catch (err) {
      console.error("❌ Delete document failed:", err.message);
      alert("ลบเอกสารล้มเหลว");
    }
  };

  // ✅ Upload รูปโปรไฟล์
  // ✅ Upload รูปโปรไฟล์ (ปรับให้ส่งทั้ง "file" และ "profile_picture" เพื่อความยืดหยุ่น)
  const handleUploadProfilePicture = async (file) => {
    if (!file) return;

    setProfilePictureUploading(true);
    try {
      const formData = new FormData();

      // 🛡️ ปลอดภัยแน่: รองรับได้ทั้งชื่อ field "file" และ "profile_picture"
      formData.append("file", file);
      formData.append("profile_picture", file); 

      const res = await uploadProfilePicture(formData);

      if (res?.profile_picture) {
        localStorage.setItem(LOCAL_STORAGE_KEY, res.profile_picture); // ⬅️ ✅ บันทึก URL
        setUser((prev) => ({
          ...prev,
          customer: {
            ...prev.customer,
            profile_picture: res.profile_picture,
          },
        }));
            
      } else {
        console.warn("⚠️ ไม่มีค่า 'profile_picture' ใน response");
        alert("อัปโหลดสำเร็จ แต่ไม่ได้รับ URL รูปใหม่จากระบบ");
      }
    } catch (err) {
      console.error("❌ Upload profile picture failed:", err?.response?.data || err.message);
      alert("อัปโหลดรูปโปรไฟล์ล้มเหลว");
    } finally {
      setProfilePictureUploading(false);
    }
  };



  const handleLogout = () => {
    if (window.confirm("คุณแน่ใจหรือไม่ว่าต้องการออกจากระบบ?")) {
      logoutUser();
      navigate("/login");
    }
  };

  return (
    <div className="profile-page">
      {/* ✅ ส่วนหัว */}
      <h2>ข้อมูลโปรไฟล์</h2>
  
      {/* ✅ รูปโปรไฟล์ */}
      <section className="profile-section">
        <ProfilePicture
          profilePictureUrl={profilePictureUrl}
          handleUploadProfilePicture={handleUploadProfilePicture}
          profilePictureUploading={profilePictureUploading}
        />
      </section>
  
      {/* ✅ ข้อมูลผู้ใช้ */}
      <section className="profile-section">
        <UserDetails
          user={user}
          handleEditProfile={() => navigate("/edit-profile")}
        />
      </section>
  
      {/* ✅ ปุ่มการจัดการโปรไฟล์ */}
      <section className="profile-section">
        <ProfileActions
          className="profile-actions"
          handlePrepareInsuranceInfo={() => navigate("/prepare-insurance-info")}
          handleReportClaim={() => navigate("/report-claim")}
          handleReviewInsurance={() => navigate("/review-insurance")}
        />
      </section>
  
      {/* ✅ เอกสารที่อัปโหลด */}
      <section className="profile-section">
        <DocumentsSection
          documents={documents}
          loadingDocuments={loadingDocuments}
          uploading={uploading}
          errorDocuments={errorDocuments}
          handleUploadDocument={handleUploadDocument}
          handleDeleteDocument={handleDeleteDocument}
          REQUIRED_DOCUMENTS={REQUIRED_DOCUMENTS}
          API_BASE_URL={process.env.REACT_APP_API_BASE_URL || window.location.origin}
          checkDocumentStatus={(type) =>
            documents.some((doc) => doc.document_type === type)
          }
        />
  
        {/* ✅ ปุ่มดูเอกสารเพิ่มเติม */}
        <div style={{ textAlign: "center", marginTop: "1.5rem" }}>
          <button
            className="view-documents-button"
            onClick={() => navigate("/uploaded-documents")}
          >
            📂 ดูเอกสารทั้งหมด
          </button>
        </div>
      </section>
  
      {/* ✅ ประวัติคำสั่งซื้อ */}
      <section className="profile-section">
        <OrderHistorySection
          orderHistory={orderHistory}
          loadingOrders={loadingOrders}
          errorOrders={errorOrders}
        />
      </section>
  
      {/* ✅ ปุ่ม logout */}
      <section className="profile-section" style={{ textAlign: "center" }}>
        <button className="logout-button" onClick={handleLogout}>
          🚪 ออกจากระบบ
        </button>
      </section>
    </div>
  );
  
  
};

export default Profile;
