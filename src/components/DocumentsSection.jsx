/*/Users/apichet/Downloads/cheetah-insurance-app/src/components/DocumentsSection.jsx */
import React from "react";
import "../assets/styles/DocumentsSection.css";

const getStatusDisplay = (status) => {
  const styles = {
    uploaded: { color: "#666" },
    verified: { color: "green", fontWeight: "bold" },
    rejected: { color: "red", fontWeight: "bold" },
  };

  return (
    <span style={styles[status] || { color: "#999" }}>
      📌 {status || "unknown"}
    </span>
  );
};

const DocumentActionButtons = ({ uploadedDoc, API_BASE_URL, handleDeleteDocument }) => {
  const filePath = uploadedDoc?.file_path || "";
  const documentId = uploadedDoc?.document_id;

  const handleView = () => {
    if (!filePath) return alert("ไม่สามารถเปิดดูเอกสารได้");
    const url = `${API_BASE_URL}/documents/uploads/${encodeURIComponent(filePath)}`;
    window.open(url, "_blank");
  };

  const handleDelete = () => {
    if (!documentId) return alert("ไม่สามารถลบเอกสารได้");
    const confirmed = window.confirm("คุณแน่ใจหรือไม่ว่าต้องการลบเอกสารนี้?");
    if (confirmed) handleDeleteDocument?.(documentId);
  };

  return (
    <>
      <button onClick={handleView} disabled={!filePath}>👁️ ดูเอกสาร</button>
      <button onClick={handleDelete} disabled={!documentId}>🗑️ ลบ</button>
    </>
  );
};

const DocumentsSection = ({
  documents = [],
  loadingDocuments = false,
  uploading = false,
  errorDocuments = "",
  handleUploadDocument,
  handleDeleteDocument,
  REQUIRED_DOCUMENTS = [],
  API_BASE_URL = "",
}) => {
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
      const uploadedDoc = documents.find(
        (d) => d.document_type === doc.type && d.file_path
      );
      console.debug(`🧾 Matching "${doc.type}" →`, uploadedDoc);
      const isUploaded = !!uploadedDoc;
      const status = uploadedDoc?.status;

      return (
        <tr key={doc.id}>
          <td>{doc.label}</td>
          <td>
          {isUploaded ? (
            <>
              ✔️ อัปโหลดแล้ว {status && getStatusDisplay(status)}
              <br />
              <small style={{ color: "#888" }}>{uploadedDoc.file_path}</small>
            </>
          ) : (
            "❌ ยังไม่ได้อัปโหลด"
          )}

          </td>
          <td>
            {!isUploaded ? (
              <input
                type="file"
                onChange={(e) => handleUploadDocument?.(e, doc.type)}
                disabled={uploading}
              />
            ) : (
              <DocumentActionButtons
                uploadedDoc={uploadedDoc}
                API_BASE_URL={API_BASE_URL}
                handleDeleteDocument={handleDeleteDocument}
              />
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
