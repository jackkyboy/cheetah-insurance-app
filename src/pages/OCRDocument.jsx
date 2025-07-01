import React, { useContext } from 'react';
import { OCRContext, OCRProvider } from '../context/OCRContext';
import UploadFile from '../components/UploadFile';

const OCRDocument = () => {
  const { ocrResult, isLoading } = useContext(OCRContext);

  return (
    <OCRProvider>
      <div>
        <h1>อัปโหลดเอกสารเพื่อทำ OCR</h1>
        <UploadFile />
        {isLoading && <p>กำลังประมวลผล...</p>}
        {ocrResult && (
          <div>
            <h3>ผลลัพธ์ OCR:</h3>
            <p>{ocrResult.text || 'ไม่พบข้อมูลที่อ่านได้'}</p>
          </div>
        )}
      </div>
    </OCRProvider>
  );
};

export default OCRDocument;
