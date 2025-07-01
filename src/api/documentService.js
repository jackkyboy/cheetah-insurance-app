/*/Users/apichet/Downloads/cheetah-insurance-app/src/api/documentService.js */
import axios from "axios";
// 📁 documentService.js
// === Constants ===
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:5000/api";

// === Token Management ===
const getAuthToken = () => localStorage.getItem("authToken");
const getRefreshToken = () => localStorage.getItem("refreshToken");
const setAuthToken = (token) => localStorage.setItem("authToken", token);
const clearTokens = () => {
  localStorage.removeItem("authToken");
  localStorage.removeItem("refreshToken");
};
const redirectToLogin = () => {
  console.warn("🚪 Logging out due to invalid or expired tokens.");
  clearTokens();
  window.location.href = "/login";
};

// === Axios Instance ===
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// === Refresh Token Logic ===
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (token) prom.resolve(token);
    else prom.reject(error);
  });
  failedQueue = [];
};

const refreshAccessToken = async () => {
  try {
    const refreshToken = getRefreshToken();
    if (!refreshToken) throw new Error("No refresh token available.");

    const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
      refresh_token: refreshToken,
    });

    const { access_token } = response.data;
    if (!access_token) throw new Error("No access token returned.");

    setAuthToken(access_token);
    console.debug("✅ Access token refreshed:", access_token);
    return access_token;
  } catch (error) {
    console.error("❌ Failed to refresh token:", error.message);
    redirectToLogin();
    throw error;
  }
};

// === Interceptors ===

// Request Interceptor: Add Authorization Header
apiClient.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      console.debug("🔗 Adding Authorization Header:", `Bearer ${token}`);
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401 Errors and Retry
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      console.warn("🔄 Token expired, attempting to refresh...");
      originalRequest._retry = true;

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return apiClient(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      isRefreshing = true;
      return new Promise((resolve, reject) => {
        refreshAccessToken()
          .then((token) => {
            console.debug("🔑 New access token:", token);
            originalRequest.headers.Authorization = `Bearer ${token}`;
            processQueue(null, token);
            resolve(apiClient(originalRequest));
          })
          .catch((err) => {
            console.error("❌ Failed to refresh token:", err.message);
            processQueue(err, null);
            redirectToLogin();
            reject(err);
          })
          .finally(() => {
            isRefreshing = false;
          });
      });
    }

    return Promise.reject(error);
  }
);

// === Document Service Functions ===

// Fetch Customer Documents
export const fetchCustomerDocuments = async (customerId) => {
  const maxRetries = 3;
  let attempts = 0;

  if (!customerId) {
    console.error("❌ [fetchCustomerDocuments] Missing customerId!");
    throw new Error("Customer ID is required.");
  }

  while (attempts < maxRetries) {
    try {
      attempts++;
      console.debug(`📡 Fetching documents for customer_id=${customerId} (Attempt ${attempts}/${maxRetries})`);

      const token = getAuthToken();
      if (!token) {
        console.error("❌ [fetchCustomerDocuments] Missing Authorization Token!");
        throw new Error("Unauthorized: No access token found.");
      }

      const response = await apiClient.get(`/documents/customer/${customerId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      console.debug("✅ [fetchCustomerDocuments] Response:", response.data);
      return response.data.documents || [];
    } catch (error) {
      console.error(`❌ [fetchCustomerDocuments] Error:`, error.response?.data || error.message);

      if (error.response?.status === 400) {
        console.error("⚠️ [fetchCustomerDocuments] 400 BAD REQUEST - Check customer_id or request format.");
        throw new Error("Invalid request. Please check customer_id.");
      }

      if (attempts >= maxRetries || error.response?.status !== 500) {
        throw new Error("Failed to fetch documents.");
      }

      console.warn(`🔄 [fetchCustomerDocuments] Retrying (${attempts}/${maxRetries})...`);
    }
  }
};

// ✅ Utility: แสดงและโยน error อย่างเป็นระบบ
const handleApiError = (label, error, fallbackMsg) => {
  console.error(`❌ ${label}:`, {
    status: error?.response?.status,
    data: error?.response?.data,
    message: error?.message,
  });
  throw new Error(error?.response?.data?.error || fallbackMsg);
};

// ✅ Upload Document
export const uploadDocument = async ({ customer_id, document_type, file }) => {
  if (!customer_id || !document_type?.trim() || !file) {
    throw new Error("กรุณาระบุข้อมูลให้ครบ: customer_id, document_type และไฟล์");
  }

  try {
    const formData = new FormData();
    formData.append("customer_id", customer_id);
    formData.append("document_type", document_type.trim());
    formData.append("file", file);

    const response = await apiClient.post("/documents", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    return response?.data?.document || response?.data;
  } catch (error) {
    handleApiError("อัปโหลดเอกสารล้มเหลว", error, "เกิดข้อผิดพลาดระหว่างการอัปโหลดเอกสาร");
  }
};

// ✅ Delete Document
export const deleteDocument = async (documentId) => {
  try {
    const response = await apiClient.delete(`/documents/${documentId}`);
    return response?.data;
  } catch (error) {
    handleApiError("ลบเอกสารล้มเหลว", error, "ไม่สามารถลบเอกสารได้");
  }
};

// ✅ Preview Document
export const previewDocument = async (documentId) => {
  try {
    const response = await apiClient.get(`/documents/preview/${documentId}`, {
      responseType: "blob",
    });
    return response?.data;
  } catch (error) {
    handleApiError("พรีวิวเอกสารล้มเหลว", error, "ไม่สามารถพรีวิวเอกสารได้");
  }
};

// ✅ OCR Processing
export const processDocumentOCR = async (documentId) => {
  try {
    const response = await apiClient.post(`/documents/process/${documentId}`);
    return response?.data;
  } catch (error) {
    handleApiError("ประมวลผล OCR ล้มเหลว", error, "ไม่สามารถประมวลผล OCR ได้");
  }
};


