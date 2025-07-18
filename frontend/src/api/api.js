// /Users/apichet/Downloads/cheetah-insurance-app/src/api/api.js
// /Users/apichet/Downloads/cheetah-insurance-app/src/api/api.js
import axios from "axios";
import { sanitizeLogoUrl } from "../utils/utils";

// Base URL ของ API
// ใส่ไว้บนสุดใต้บรรทัดนี้เลย:
const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL ||
  (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://localhost:5000/api"
    : `http://${window.location.hostname}:5000/api`);

console.log("🌍 API_BASE_URL =", API_BASE_URL); // ✅ ใส่บรรทัดนี้ไว้ตอน build


// ฟังก์ชันจัดการ Token
const getToken = () => {
    try {
        return localStorage.getItem("authToken") || null;
    } catch (error) {
        console.warn("⚠️ localStorage not accessible:", error);
        return null;
    }
};

const getRefreshToken = () => {
    try {
        return localStorage.getItem("refreshToken") || null;
    } catch (error) {
        console.warn("⚠️ localStorage not accessible:", error);
        return null;
    }
};

const saveTokens = (accessToken, refreshToken) => {
    try {
        localStorage.setItem("authToken", accessToken);
        if (refreshToken) localStorage.setItem("refreshToken", refreshToken);
    } catch (error) {
        console.error("❌ Failed to save tokens:", error);
    }
};

const clearTokens = () => {
    try {
        localStorage.removeItem("authToken");
        localStorage.removeItem("refreshToken");
        console.warn("🔐 Tokens cleared. Redirecting to login...");
        setTimeout(() => (window.location.href = "/login"), 500);
    } catch (error) {
        console.error("❌ Error clearing tokens:", error);
    }
};

// ฟังก์ชันสำหรับ Refresh Token
const isTokenExpired = (token) => {
    if (!token) return true;
    try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        return payload.exp * 1000 < Date.now(); // เปรียบเทียบเวลา expiry
    } catch (e) {
        return true; // Token ไม่ถูกต้อง
    }
};

const refreshAccessToken = async () => {
    try {
        const refreshToken = getRefreshToken();
        if (!refreshToken || isTokenExpired(refreshToken)) {
            console.warn("❌ Refresh token expired. Logging out...");
            clearTokens();
            return null;
        }

        console.debug("🔄 Attempting to refresh access token...");
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
        });

        const { access_token, refresh_token: newRefreshToken } = response.data;
        console.log("✅ Access token refreshed successfully.");

        saveTokens(access_token, newRefreshToken);
        return access_token;
    } catch (error) {
        console.error("❌ Failed to refresh token:", error.message);
        clearTokens();
        throw error;
    }
};

// Queue สำหรับ Retry Requests ระหว่าง Refresh Token
let isRefreshing = false;
let failedRequestsQueue = [];

// สร้าง Axios Instance
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: { "Content-Type": "application/json" },
});

// Interceptor สำหรับ Request: เพิ่ม Authorization Header
api.interceptors.request.use(
    (config) => {
        const token = getToken();
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Interceptor สำหรับ Response: จัดการ 401 Unauthorized
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            if (isRefreshing) {
                return new Promise((resolve, reject) => {
                    failedRequestsQueue.push({ resolve, reject });
                }).then((token) => {
                    originalRequest.headers.Authorization = `Bearer ${token}`;
                    return api(originalRequest);
                });
            }

            isRefreshing = true;

            try {
                const newAccessToken = await refreshAccessToken();
                if (!newAccessToken) {
                    console.warn("🔴 Refresh token failed. Logging out...");
                    clearTokens();
                    return Promise.reject(error);
                }

                failedRequestsQueue.forEach((prom) => prom.resolve(newAccessToken));
                failedRequestsQueue = [];

                originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
                return api(originalRequest);
            } catch (refreshError) {
                console.error("❌ Refresh token request failed:", refreshError.message);
                failedRequestsQueue.forEach((prom) => prom.reject(refreshError));
                failedRequestsQueue = [];

                clearTokens();
                return Promise.reject(refreshError);
            } finally {
                isRefreshing = false;
            }
        }

        return Promise.reject(error);
    }
);


export const testConnection = async () => {
    try {
        const response = await api.get("/health");
        console.log("🟢 API Health Check:", response.data);
    } catch (error) {
        console.error("❌ API test failed:", error.message);
    }
};

// ✅ แก้ไขการตรวจสอบตัวแปร filters
export const fetchInsurancePackages = async (filters) => {
    if (!filters || typeof filters !== "object" || Object.keys(filters).length === 0) {
        console.error("❌ [fetchInsurancePackages] Invalid filters:", filters);
        throw new Error("Filters must be a valid object and cannot be empty.");
    }
    try {
        console.log("📤 Fetching insurance packages with filters:", JSON.stringify(filters));
        const response = await api.post("/bigquery/query", filters);
        return response.data;
    } catch (error) {
        console.error("❌ Error fetching insurance packages:", error.response?.data || error.message);
        throw error;
    }
};


// ✅ ป้องกันข้อผิดพลาดจาก packageCode ที่เป็น null หรือ undefined
export const fetchCoverageData = async (packageCode) => {
    if (!packageCode) {
        console.error("❌ [fetchCoverageData] Missing packageCode.");
        throw new Error("packageCode is required for fetching coverage data.");
    }
    try {
        console.log(`📡 [fetchCoverageData] Fetching coverage data for package: ${packageCode}`);
        const response = await api.get(`/insurance-options/insurance_coverage`, {
            params: { package_code: packageCode }
        });

        if (!response.data.coverage) {
            console.warn(`⚠️ [fetchCoverageData] No coverage data found for package: ${packageCode}`);
            return null;
        }

        console.log("✅ [fetchCoverageData] Coverage data loaded:", response.data.coverage);
        return response.data.coverage;
    } catch (error) {
        console.error("❌ [fetchCoverageData] Error fetching coverage:", error.message);
        throw error;
    }
};

// ✅ แก้ไข fetchPackagesWithLogos ให้รองรับข้อผิดพลาดจาก API
export const fetchPackagesWithLogos = async () => {
    try {
        console.log("📤 Fetching insurance packages with logos...");
        const response = await api.get("/car-options/packages_with_logos");
        const results = response.data?.results || [];
        return results.map((item) => ({
            ...item,
            logo_url: sanitizeLogoUrl(item.logo_url),
        }));
    } catch (error) {
        console.error("❌ Error fetching packages with logos:", error.message);
        throw error;
    }
};

export default api;
