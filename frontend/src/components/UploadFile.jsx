/*/Users/apichet/Downloads/cheetah-insurance-app/src/components/UploadFile.jsx */
import React, { useState, useContext } from "react";
import { uploadDocumentForOCR } from "../api/ocrService";
import { OCRContext } from "../context/OCRContext";

const UploadFile = () => {
  const [file, setFile] = useState(null); // สำหรับเก็บไฟล์ที่เลือก
  const [error, setError] = useState(""); // สำหรับเก็บข้อความข้อผิดพลาด
  const [uploadProgress, setUploadProgress] = useState(0); // สำหรับแสดงความคืบหน้าการอัปโหลด
  const { updateOCRResult, toggleLoading } = useContext(OCRContext);

  const MAX_FILE_SIZE_MB = 5; // กำหนดขนาดไฟล์สูงสุด 5MB
  const ALLOWED_TYPES = ["image/png", "image/jpeg", "image/jpg", "application/pdf"]; // ประเภทไฟล์ที่รองรับ

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];

    if (selectedFile) {
      const fileSizeMB = selectedFile.size / (1024 * 1024); // แปลงขนาดไฟล์เป็น MB

      if (!ALLOWED_TYPES.includes(selectedFile.type)) {
        setError("รองรับเฉพาะไฟล์รูปภาพ (PNG, JPEG) หรือ PDF เท่านั้น");
        setFile(null);
        return;
      }

      if (fileSizeMB > MAX_FILE_SIZE_MB) {
        setError(`ขนาดไฟล์ต้องไม่เกิน ${MAX_FILE_SIZE_MB} MB`);
        setFile(null);
        return;
      }

      setError(""); // เคลียร์ข้อผิดพลาด
      setFile(selectedFile); // เก็บไฟล์ที่เลือก
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert("กรุณาเลือกไฟล์ที่ถูกต้องก่อน");
      return;
    }

    toggleLoading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const result = await uploadDocumentForOCR(formData, {
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(percentCompleted);
        },
      });

      updateOCRResult(result);
      setError("");
      alert("อัปโหลดไฟล์สำเร็จ");
    } catch (error) {
      console.error("Error uploading file:", error.message);
      setError("เกิดข้อผิดพลาดในการอัปโหลดไฟล์");
      alert("เกิดข้อผิดพลาดในการอัปโหลด");
    } finally {
      toggleLoading(false);
      setFile(null); // รีเซ็ตไฟล์ที่เลือก
      setUploadProgress(0); // รีเซ็ตสถานะความคืบหน้า
    }
  };

  return (
    <div className="upload-container">
      <h3>อัปโหลดเอกสารเพื่อประมวลผล OCR</h3>

      <input
        type="file"
        onChange={handleFileChange}
        accept={ALLOWED_TYPES.join(",")}
      />

      {error && <p style={{ color: "red" }}>{error}</p>}

      {uploadProgress > 0 && (
        <p style={{ color: "blue" }}>
          ⏳ กำลังอัปโหลด... {uploadProgress}%
        </p>
      )}

      <button onClick={handleUpload} disabled={!file}>
        อัปโหลดเอกสาร
      </button>

      {file && (
        <p>
          📄 ไฟล์ที่เลือก: <strong>{file.name}</strong>
        </p>
      )}
    </div>
  );
};

export default UploadFile;
