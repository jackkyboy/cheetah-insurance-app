// /Users/apichet/Downloads/cheetah-insurance-app/src/api/axiosInstance.js
// src/api/axiosInstance.js

import axios from "axios";
import { 
  getAuthToken, 
  getRefreshToken, 
  refreshAccessToken, 
  saveAuthToken,
  clearTokens 
} from "./authService";

// ✅ ใช้ baseURL จาก .env ที่ถูก inject ตอน build
const BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:5000/api";

console.log("🌐 axiosInstance BASE_URL =", BASE_URL);

const axiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
});

// 🔄 สำหรับ refresh token
let isRefreshing = false;
let refreshSubscribers = [];

const subscribeTokenRefresh = (cb) => refreshSubscribers.push(cb);
const onRefreshed = (token) => {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
};

// ✅ Request Interceptor
axiosInstance.interceptors.request.use(
  async (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ✅ Response Interceptor
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
