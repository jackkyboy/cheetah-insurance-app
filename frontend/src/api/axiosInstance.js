// /Users/apichet/Downloads/cheetah-insurance-app/src/api/axiosInstance.js
import axios from "axios";
import { 
  getAuthToken, 
  getRefreshToken, 
  refreshAccessToken, 
  saveAuthToken,
  clearTokens 
} from "./authService";

// ✅ baseURL ถูก set ผ่าน .env.production ระหว่าง build
const BASE_URL = import.meta.env?.REACT_APP_API_BASE_URL || process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:5000/api";

console.log("🌐 axiosInstance BASE_URL =", BASE_URL); // ลอง log ดูว่ามาไหม (dev only)

const axiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
});

// ========== ✅ Global Refresh Token Handling ==========
let isRefreshing = false;
let refreshSubscribers = [];

const subscribeTokenRefresh = (cb) => refreshSubscribers.push(cb);
const onRefreshed = (token) => {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
};

// ========== ✅ Request Interceptor ==========
axiosInstance.interceptors.request.use(
  async (config) => {
    let token = getAuthToken();
    if (!token && !isRefreshing) {
      isRefreshing = true;
      token = await refreshAccessToken();
      isRefreshing = false;
      if (token) saveAuthToken(token);
    }

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    } else {
      console.warn("⚠️ No token available, sending unauthenticated request.");
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// ========== ✅ Response Interceptor ==========
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (isRefreshing) {
        return new Promise((resolve) => {
          subscribeTokenRefresh((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            resolve(axiosInstance(originalRequest));
          });
        });
      }

      try {
        isRefreshing = true;
        const newToken = await refreshAccessToken();
        isRefreshing = false;

        if (!newToken) {
          clearTokens();
          return Promise.reject(error);
        }

        saveAuthToken(newToken);
        onRefreshed(newToken);

        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return axiosInstance(originalRequest);
      } catch (err) {
        clearTokens();
        return Promise.reject(err);
      }
    }

    return Promise.reject(error);
  }
);

export default axiosInstance;
