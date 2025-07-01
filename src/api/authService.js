/* /Users/apichet/Downloads/cheetah-insurance-app/src/api/authService.js */
import axios from "axios";
import { jwtDecode } from "jwt-decode";
import { saveAdminAuthToken, saveAdminRefreshToken } from "./adminAuthService";

// ✅ กำหนดค่า BASE URL
const BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:5000/api";
console.log("🚀 Using API BASE URL:", BASE_URL);

// ✅ กำหนดคีย์ที่ใช้เก็บ Token ใน LocalStorage
const AUTH_TOKEN_KEY = "authToken";
const REFRESH_TOKEN_KEY = "refreshToken";
const USER_ROLE_KEY = "userRole";

// ✅ ฟังก์ชันดึง Token
export const getAuthToken = () => localStorage.getItem(AUTH_TOKEN_KEY);
export const getRefreshToken = () => localStorage.getItem(REFRESH_TOKEN_KEY);
export const getUserRole = () => localStorage.getItem(USER_ROLE_KEY);

// ✅ ฟังก์ชันบันทึก Token
export const saveAuthToken = (token) => {
  if (token) {
    const decodedToken = jwtDecode(token);
    const role = decodedToken?.role || "user";
    if (role === "admin") {
      saveAdminAuthToken(token);
    } else {
      localStorage.setItem(AUTH_TOKEN_KEY, token);
    }
  }
};

export const saveRefreshToken = (token) => {
  if (token) {
    const decodedToken = jwtDecode(token);
    const role = decodedToken?.role || "user";
    if (role === "admin") {
      saveAdminRefreshToken(token);
    } else {
      localStorage.setItem(REFRESH_TOKEN_KEY, token);
    }
  }
};

export const saveUserRole = (role) => {
  if (role) {
    localStorage.setItem(USER_ROLE_KEY, role);
  }
};

// ✅ ฟังก์ชันเคลียร์ Token
export const clearTokens = () => {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_ROLE_KEY);
  window.location.href = "/login";
};

// ✅ สร้าง Axios Instance
const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// ✅ ฟังก์ชัน Refresh Token
export const refreshAccessToken = async () => {
  try {
    const refreshToken = getRefreshToken();
    console.log("🔄 [refreshAccessToken] Attempting to refresh token with:", refreshToken);

    if (!refreshToken) {
      console.warn("❌ [refreshAccessToken] No refresh token found. Logging out...");
      return null;
    }

    const response = await axios.post(`${BASE_URL}/auth/refresh`, { refresh_token: refreshToken });
    console.log("✅ [refreshAccessToken] Token refreshed successfully:", response.data);

    if (!response.data?.access_token) {
      console.error("❌ [refreshAccessToken] No access token received.");
      return null;
    }

    saveAuthToken(response.data.access_token);
    saveRefreshToken(response.data.refresh_token || refreshToken); // บันทึก Refresh Token ใหม่ (ถ้ามี)
    return response.data.access_token;
  } catch (error) {
    console.error("❌ [refreshAccessToken] Refresh failed:", error.response?.data || error.message);
    return null;
  }
};


// ✅ Interceptor สำหรับแนบ Token ใน Request
apiClient.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ✅ จัดการ Refresh Token แบบอัตโนมัติ
let isRefreshing = false;
let refreshSubscribers = [];

function onRefreshed(newToken) {
  refreshSubscribers.forEach((callback) => callback(newToken));
  refreshSubscribers = [];
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    console.warn(`[Interceptor] API Error: ${error.response?.status}`, error.response?.data || error.message);

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (!isRefreshing) {
        isRefreshing = true;
        console.log("🔄 [Interceptor] Refreshing token...");
        const newAccessToken = await refreshAccessToken();
        isRefreshing = false;
        if (!newAccessToken) {
          console.error("❌ [Interceptor] Refresh token failed. Logging out.");
          clearTokens();
          return Promise.reject(error);
        }

        console.log("✅ [Interceptor] Using new access token:", newAccessToken);
        saveAuthToken(newAccessToken);
        onRefreshed(newAccessToken);
      }

      return new Promise((resolve, reject) => {
        refreshSubscribers.push((newToken) => {
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          resolve(apiClient(originalRequest));
        });
      });
    }

    return Promise.reject(error);
  }
);


// ✅ ฟังก์ชัน Login
export const login = async (email, password) => {
  try {
    const response = await apiClient.post(`/auth/login`, { email, password });

    if (!response.data?.access_token || !response.data?.refresh_token || !response.data?.user?.role) {
      throw new Error("Invalid login response.");
    }

    saveAuthToken(response.data.access_token);
    saveRefreshToken(response.data.refresh_token);
    saveUserRole(response.data.user.role || "user");

    return {
      access_token: response.data.access_token,
      refresh_token: response.data.refresh_token,
      role: response.data.user.role
    };

  } catch (err) {
    console.error("❌ Login failed:", err.response?.data || err.message);
    throw err;
  }
};

// ✅ ฟังก์ชัน Logout
export const logout = () => clearTokens();

// ✅ ฟังก์ชันดึงข้อมูลผู้ใช้ที่ล็อกอินอยู่
export const fetchAuthenticatedUser = async () => {
  try {
    const { data } = await apiClient.get(`/user/profile`);
    return data;
  } catch (err) {
    throw err;
  }
};

// ✅ ฟังก์ชัน Register
export const register = async (userData) => {
  try {
    const { data } = await apiClient.post(`/auth/register`, userData);
    return data;
  } catch (err) {
    throw err;
  }
};

// ✅ ฟังก์ชัน Request Password Reset
export const requestPasswordReset = async (email) => {
  try {
    const response = await apiClient.post(`/auth/forgot-password`, { email });
    return response.data;
  } catch (error) {
    throw error;
  }
};

// ✅ ฟังก์ชัน Reset Password
export const resetPassword = async (token, newPassword) => {
  try {
    const response = await apiClient.post(`/auth/reset-password`, { token, new_password: newPassword });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export default apiClient;
