// /src/components/DocumentsSection.jsx
import React from "react";
import PropTypes from "prop-types";
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
    if (window.confirm("คุณแน่ใจหรือไม่ว่าต้องการลบเอกสารนี้?")) {
      handleDeleteDocument?.(documentId);
    }
  };

  return (
    <>
      <button onClick={handleView} disabled={!filePath}>👁️ ดูเอกสาร</button>
      <button onClick={handleDelete} disabled={!documentId}>🗑️ ลบ</button>
    </>
  );
};

DocumentActionButtons.propTypes = {
  uploadedDoc: PropTypes.object.isRequired,
  API_BASE_URL: PropTypes.string.isRequired,
  handleDeleteDocument: PropTypes.func.isRequired,
};

const DocumentRow = ({
  doc,
  uploadedDoc,
  uploading,
  handleUploadDocument,
  API_BASE_URL,
  handleDeleteDocument,
}) => {
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
};

DocumentRow.propTypes = {
  doc: PropTypes.object.isRequired,
  uploadedDoc: PropTypes.object,
  uploading: PropTypes.bool,
  handleUploadDocument: PropTypes.func,
  API_BASE_URL: PropTypes.string.isRequired,
  handleDeleteDocument: PropTypes.func.isRequired,
};

const DocumentsSection = ({
  documents,
  loadingDocuments,
  uploading,
  errorDocuments,
  handleUploadDocument,
  handleDeleteDocument,
  REQUIRED_DOCUMENTS,
  API_BASE_URL,
}) => {
  const renderDocumentRows = () => {
    if (!REQUIRED_DOCUMENTS?.length) {
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
      return (
        <DocumentRow
          key={doc.id}
          doc={doc}
          uploadedDoc={uploadedDoc}
          uploading={uploading}
          handleUploadDocument={handleUploadDocument}
          API_BASE_URL={API_BASE_URL}
          handleDeleteDocument={handleDeleteDocument}
        />
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

DocumentsSection.propTypes = {
  documents: PropTypes.array.isRequired,
  loadingDocuments: PropTypes.bool,
  uploading: PropTypes.bool,
  errorDocuments: PropTypes.string,
  handleUploadDocument: PropTypes.func,
  handleDeleteDocument: PropTypes.func,
  REQUIRED_DOCUMENTS: PropTypes.array,
  API_BASE_URL: PropTypes.string,
};

DocumentsSection.defaultProps = {
  documents: [],
  loadingDocuments: false,
  uploading: false,
  errorDocuments: "",
  REQUIRED_DOCUMENTS: [],
  API_BASE_URL: "",
};

export default DocumentsSection;

