// src/pages/UploadedDocumentsPage.jsx
import React, { useEffect, useState } from "react";
import { fetchCustomerDocuments } from "../api/documentService";
import "../assets/styles/UploadDocument.css";

const DOCUMENT_LABELS = {
  identity_card: "สำเนาบัตรประชาชนเจ้าของรถ",
  driver_license_owner: "สำเนาใบขับขี่เจ้าของรถ",
  car_registration: "สำเนาหนังสือการจดทะเบียนรถยนต์",
  current_policy: "สำเนากรมธรรม์หรือใบเตือนต่ออายุประกันรถยนต์ในปัจจุบัน",
  renewal_reminder: "เอกสารใบเตือนการต่อประกัน",
  driver_license: "ใบขับขี่",
};

const REQUIRED_DOC_TYPES = Object.keys(DOCUMENT_LABELS);

const UploadedDocumentsPage = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAll, setShowAll] = useState(false);
  const customerId = localStorage.getItem("customer_id");

  // 📦 จัดเรียงเอกสารทั้งหมด โดยเติมเอกสารที่ยังไม่อัปโหลด
  const buildFullDocumentList = (rawDocs = []) => {
    const latestDocsMap = {};
    for (const doc of rawDocs) {
      const { document_type, uploaded_at } = doc;
      if (
        !latestDocsMap[document_type] ||
        new Date(uploaded_at) > new Date(latestDocsMap[document_type].uploaded_at)
      ) {
        latestDocsMap[document_type] = doc;
      }
    }
  
    return REQUIRED_DOC_TYPES.map((type) => {
      const found = latestDocsMap[type];
      return found
        ? found // 🟢 ใช้ status จริงจาก database เช่น 'verified', 'rejected'
        : { document_type: type, status: "missing" };
    });
  };
  

  useEffect(() => {
    const load = async () => {
      try {
        const result = await fetchCustomerDocuments(customerId);
        const enriched = buildFullDocumentList(result);
        setDocuments(enriched);
      } catch (e) {
        console.error("❌ โหลดเอกสารล้มเหลว:", e.message);
        setDocuments([]);
      } finally {
        setLoading(false);
      }
    };

    if (customerId) load();
  }, [customerId]);

  const formatDate = (raw) => {
    if (!raw) return "-";
    const d = new Date(raw);
    return d.toLocaleDateString("th-TH", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  };

  return (
    <div className="upload-documents-page">
      <h2 className="page-title">📁 เอกสารลูกค้า</h2>

      {loading ? (
        <div className="loading">⏳ กำลังโหลดข้อมูล...</div>
      ) : documents.length === 0 ? (
        <div className="no-documents">📭 ยังไม่มีรายการเอกสาร</div>
      ) : (
        <>
          <div className="document-list">
            {(showAll ? documents : documents.slice(0, 3)).map((doc, i) => (
              <div key={i} className={`doc-card ${doc.status}`}>
                <div className="doc-card-icon">📄</div>

                <div className="doc-card-info">
                  <div className="doc-card-title">
                    {DOCUMENT_LABELS[doc.document_type] || doc.document_type}
                  </div>
                </div>

                <div className="doc-card-status">
                  {doc.status === "missing" ? (
                    <span className="status-missing">❌ ยังไม่อัปโหลด</span>
                  ) : (
                    <>
                      <span className={`status-${doc.status}`}>
                        {doc.status === "verified" && "✅ ยืนยันแล้ว"}
                        {doc.status === "uploaded" && "✔ อัปโหลดแล้ว"}
                        {doc.status === "rejected" && "🚫 ถูกปฏิเสธ"}
                        {!["verified", "uploaded", "rejected"].includes(doc.status) && "📌 ไม่ทราบสถานะ"}
                      </span>
                      <br />
                      <small>{formatDate(doc.uploaded_at)}</small>
                    </>
                  )}
                </div>

              </div>
            ))}
          </div>

          {documents.length > 3 && (
            <div className="toggle-wrapper">
              <button className="toggle-button" onClick={() => setShowAll(!showAll)}>
                {showAll ? "🔽 ซ่อนรายการ" : "🔼 แสดงทั้งหมด"}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default UploadedDocumentsPage;
