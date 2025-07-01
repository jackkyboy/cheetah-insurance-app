import axios from './axios';

// ฟังก์ชันสำหรับอัปโหลดเอกสารเพื่อทำ OCR/Users/apichet/Downloads/cheetah-insurance-app/src/api/ocrService.js
export const uploadDocumentForOCR = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post('/api/ocr/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data; // ผลลัพธ์ OCR
  } catch (error) {
    console.error('OCR upload error:', error);
    throw error;
  }
};
