import React, { createContext, useState } from 'react';

export const OCRContext = createContext();

export const OCRProvider = ({ children }) => {
  const [ocrResult, setOcrResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const updateOCRResult = (result) => setOcrResult(result);
  const toggleLoading = (status) => setIsLoading(status);

  return (
    <OCRContext.Provider value={{ ocrResult, updateOCRResult, isLoading, toggleLoading }}>
      {children}
    </OCRContext.Provider>
  );
};
