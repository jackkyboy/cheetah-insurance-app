// /Users/apichet/Downloads/cheetah-insurance-app/src/api/adminAuthService.js
import axios from "axios";
import { jwtDecode } from "jwt-decode";

// ✅ Base URL for Backend API
const BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:5000/api";

// ✅ Token Keys
const AUTH_TOKEN_KEY = "adminAuthToken";
const REFRESH_TOKEN_KEY = "adminRefreshToken";

// ✅ ตัวแปรควบคุมป้องกัน Loop
let isRefreshing = false;
let isLoggingOut = false;
let refreshSubscribers = [];
let retryCount = 0;
const maxRetryCount = 3; // จำกัดจำนวนครั้งที่ Refresh Token ได้

// ✅ ฟังก์ชัน Subscribe Token Refresh
const subscribeTokenRefresh = (cb) => {
    refreshSubscribers.push(cb);
};
const onRefreshed = (token) => {
    refreshSubscribers.forEach((cb) => cb(token));
    refreshSubscribers = [];
};

// ✅ ฟังก์ชันดึง Token
export const getAuthToken = () => localStorage.getItem(AUTH_TOKEN_KEY);
export const getRefreshToken = () => localStorage.getItem(REFRESH_TOKEN_KEY);

// ✅ ฟังก์ชันบันทึก Token (กลับมาตามเดิม)
export const saveAuthToken = (token) => {
    if (token) localStorage.setItem(AUTH_TOKEN_KEY, token);
};
export const saveRefreshToken = (token) => {
    if (token) localStorage.setItem(REFRESH_TOKEN_KEY, token);
};

// ✅ **เพิ่มฟังก์ชันเดิมกลับมา**
export const saveAdminAuthToken = (token, refreshToken) => {
    if (token) localStorage.setItem(AUTH_TOKEN_KEY, token);
    if (refreshToken) localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
};
export const saveAdminRefreshToken = (token) => {
    if (token) localStorage.setItem(REFRESH_TOKEN_KEY, token);
};

// ✅ ฟังก์ชันตรวจสอบว่า Token หมดอายุหรือไม่
export const isTokenExpired = (token) => {
    if (!token) return true;
    try {
        const decoded = jwtDecode(token);
        return decoded.exp < Date.now() / 1000;
    } catch (err) {
        return true;
    }
};

// ✅ ป้องกัน Redirect Loop
export const clearAdminSession = () => {
    if (isLoggingOut) return;
    isLoggingOut = true;

    console.warn("🛑 [clearAdminSession] Logging out...");

    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);

    setTimeout(() => {
        if (window.location.pathname !== "/admin/login") {
            window.location.href = "/admin/login"; // ✅ เปลี่ยนจาก `replace()` เป็น `href` เพื่อให้ React Router รีโหลด
        }
        isLoggingOut = false;
    }, 500);
};

// /Users/apichet/Downloads/cheetah-insurance-app/src/api/adminAuthService.js
// ✅ Refresh Token Logic (แก้ไขป้องกัน Refresh Loop)
// ✅ Refresh Token Logic (แก้ไขป้องกัน Refresh Loop)
export const refreshAccessToken = async () => {
    if (isRefreshing) {
        return new Promise((resolve) => {
            subscribeTokenRefresh((token) => resolve(token));
        });
    }

    isRefreshing = true;
    try {
        const refreshToken = getRefreshToken();
        if (!refreshToken) {
            console.warn("❌ [refreshAccessToken] ไม่มี Refresh Token, ไม่สามารถรีเฟรช!");
            isRefreshing = false;
            return null;
        }

        console.log("🔄 [refreshAccessToken] Trying to refresh token...");
        const { data } = await axios.post(`${BASE_URL}/auth/refresh`, { refresh_token: refreshToken });

        if (!data.access_token) {
            console.error("❌ [refreshAccessToken] ไม่สามารถรีเฟรช Token ได้");
            isRefreshing = false;
            return null;
        }

        saveAuthToken(data.access_token);
        isRefreshing = false;
        retryCount = 0; // ✅ รีเซ็ต Retry Count ถ้า Refresh สำเร็จ

        onRefreshed(data.access_token);
        return data.access_token;
    } catch (error) {
        console.error("❌ [refreshAccessToken] Refresh Token ล้มเหลว!");
        isRefreshing = false;
        return null;
    }
};




// ✅ Create Axios Instance
const adminApiClient = axios.create({
    baseURL: BASE_URL,
    headers: { "Content-Type": "application/json" },
});

// ✅ Request Interceptor (เพิ่ม Token ในทุก Request)
adminApiClient.interceptors.request.use(async (config) => {
    let token = getAuthToken();

    if (!token || isTokenExpired(token)) {
        if (retryCount >= maxRetryCount) {
            console.warn("❌ Too many refresh attempts, logging out...");
            clearAdminSession();
            return Promise.reject("Too many refresh attempts");
        }

        retryCount += 1;
        token = await refreshAccessToken();
        if (!token) return Promise.reject("No valid token.");
    }

    config.headers.Authorization = `Bearer ${token}`;
    return config;
}, (error) => Promise.reject(error));


// ✅ Response Interceptor (ถ้า Token หมดอายุ ให้ Refresh)
adminApiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            if (retryCount >= maxRetryCount) {
                console.warn("❌ Token refresh failed, too many attempts");
                clearAdminSession();
                return Promise.reject("Token refresh failed");
            }

            retryCount += 1;
            const newToken = await refreshAccessToken();
            if (newToken) {
                originalRequest.headers.Authorization = `Bearer ${newToken}`;
                return adminApiClient(originalRequest);
            } else {
                clearAdminSession();
            }
        }

        return Promise.reject(error);
    }
);

// ✅ ฟังก์ชัน Login สำหรับ Admin
export const adminLogin = async (email, password) => {
    try {
        const { data } = await axios.post(`${BASE_URL}/admins/login`, { email, password });

        if (!data?.access_token || !data?.refresh_token) {
            throw new Error("Invalid Login Response: Missing Tokens.");
        }

        saveAuthToken(data.access_token);
        saveRefreshToken(data.refresh_token);
        saveAdminAuthToken(data.access_token, data.refresh_token); // ✅ ใช้ฟังก์ชันเดิม

        return { access_token: data.access_token, refresh_token: data.refresh_token };
    } catch (err) {
        throw err;
    }
};

// ✅ Logout Admin
export const adminLogout = () => {
    clearAdminSession();
};

// ✅ ดึงข้อมูล Admin ที่ล็อกอินอยู่
export const fetchAuthenticatedAdmin = async () => {
    try {
        const { data } = await adminApiClient.get("/admins/me");
        return data;
    } catch (err) {
        if (err.response?.status === 401) clearAdminSession();
        throw err;
    }
};

export default adminApiClient;
