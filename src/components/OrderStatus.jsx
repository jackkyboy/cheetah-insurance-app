/*/Users/apichet/Downloads/cheetah-insurance-app/src/components/OrderStatus.jsx */
import React from "react";

const DocumentsSection = ({
  documents = [],
  loadingDocuments = false,
  uploading = false,
  errorDocuments = "",
  handleUploadDocument,
  handleDeleteDocument,
  checkDocumentStatus,
  REQUIRED_DOCUMENTS = [],
  API_BASE_URL = "",
}) => {
  // ฟังก์ชันสำหรับเรนเดอร์แถวของเอกสาร
  const renderDocumentRows = () => {
    if (!REQUIRED_DOCUMENTS.length) {
      return (
        <tr>
          <td colSpan="3" style={{ textAlign: "center" }}>
            🛑 ไม่มีรายการเอกสารที่ต้องการ
          </td>
        </tr>
      );
    }

    return REQUIRED_DOCUMENTS.map((doc) => {
      const isUploaded = checkDocumentStatus?.(doc.type) || false;
      const uploadedDoc = documents.find((d) => d.document_type === doc.type);

      return (
        <tr key={doc.id}>
          <td>{doc.label}</td>
          <td>{isUploaded ? "✔️ อัปโหลดแล้ว" : "❌ ยังไม่ได้อัปโหลด"}</td>
          <td>
            {!isUploaded ? (
              <input
                type="file"
                onChange={(e) => handleUploadDocument?.(e, doc.type)}
                disabled={uploading}
              />
            ) : (
              <>
                <button
                  onClick={() => {
                    if (uploadedDoc?.file_path) {
                      const url = `${API_BASE_URL}/documents/uploads/${encodeURIComponent(
                        uploadedDoc.file_path
                      )}`;
                      window.open(url, "_blank");
                    } else {
                      alert("ไม่สามารถเปิดดูเอกสารได้");
                    }
                  }}
                  disabled={!uploadedDoc?.file_path}
                >
                  👁️ ดูเอกสาร
                </button>
                <button
                  onClick={() => {
                    if (uploadedDoc?.document_id) {
                      if (window.confirm("คุณแน่ใจหรือไม่ว่าต้องการลบเอกสารนี้?")) {
                        handleDeleteDocument?.(uploadedDoc.document_id);
                      }
                    } else {
                      alert("ไม่สามารถลบเอกสารได้");
                    }
                  }}
                  disabled={!uploadedDoc?.document_id}
                >
                  🗑️ ลบ
                </button>
              </>
            )}
          </td>
        </tr>
      );
    });
  };

  return (
    <div className="documents-card">
      {errorDocuments && (
        <p className="error-message" style={{ color: "red" }}>
          ❌ {errorDocuments}
        </p>
      )}

      {uploading && <p>⏳ กำลังอัปโหลด...</p>}

      {loadingDocuments ? (
        <p>⏳ กำลังโหลดเอกสาร...</p>
      ) : (
        <table className="documents-table">
          <thead>
            <tr>
              <th>รายการเอกสาร</th>
              <th>สถานะ</th>
              <th>การดำเนินการ</th>
            </tr>
          </thead>
          <tbody>{renderDocumentRows()}</tbody>
        </table>
      )}
    </div>
  );
};

export default DocumentsSection;
