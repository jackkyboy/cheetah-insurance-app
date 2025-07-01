// /Users/apichet/Downloads/cheetah-insurance-app/src/api/axiosInstance.js
import axios from "axios";
import { 
    getAuthToken, 
    getRefreshToken, 
    refreshAccessToken, 
    saveAuthToken,
    clearTokens  // แทนที่ clearAdminSession ให้ตรงกับ authService.js
} from "./authService";

const BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:5000/api";

const axiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
});

// ✅ Global Refresh Token Handling
let isRefreshing = false;
let refreshSubscribers = [];

const subscribeTokenRefresh = (cb) => {
  refreshSubscribers.push(cb);
};

const onRefreshed = (token) => {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
};

// ✅ Request Interceptor: Attach JWT Token
axiosInstance.interceptors.request.use(
  async (config) => {
    let token = getAuthToken();
    console.log(`[${new Date().toISOString()}] 🔎 Checking Auth Token...`, token);

    if (!token) {
      console.warn(`[${new Date().toISOString()}] ⚠️ No Auth Token found! Checking refresh token...`);

      if (!isRefreshing) {
        isRefreshing = true;
        token = await refreshAccessToken();
        isRefreshing = false;
      }

      if (!token) {
        console.error(`[${new Date().toISOString()}] ❌ Refresh failed. Logging out.`);
        clearTokens();
        return Promise.reject(new Error("Authentication required"));
      }

      saveAuthToken(token);
    }

    config.headers.Authorization = `Bearer ${token}`;
    console.log(`[${new Date().toISOString()}] ✅ Sending Request with Token:`, config.headers.Authorization);

    return config;
  },
  (error) => Promise.reject(error)
);


// ✅ Response Interceptor: Handle Token Expiration (401 Unauthorized)
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      console.warn(`[${new Date().toISOString()}] ⚠️ [Interceptor] 401 Unauthorized detected. Trying to refresh token...`);

      originalRequest._retry = true;

      if (isRefreshing) {
        console.warn(`[${new Date().toISOString()}] 🚀 [Interceptor] Waiting for token refresh...`);
        return new Promise((resolve) => {
          subscribeTokenRefresh((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            resolve(axiosInstance(originalRequest));
          });
        });
      }

      isRefreshing = true;

      try {
        const newToken = await refreshAccessToken();
        isRefreshing = false;

        if (!newToken) {
          console.error(`[${new Date().toISOString()}] ❌ [Interceptor] Refresh token failed. Clearing session...`);
          clearTokens();
          return Promise.reject(error);
        }

        console.log(`[${new Date().toISOString()}] ✅ [Interceptor] Using New Access Token:`, newToken);

        saveAuthToken(newToken);
        onRefreshed(newToken);

        originalRequest.headers["Authorization"] = `Bearer ${newToken}`;
        return axiosInstance(originalRequest);
      } catch (refreshError) {
        console.error(`[${new Date().toISOString()}] ❌ [Interceptor] Refresh process failed:`, refreshError);
        clearTokens();
        return Promise.reject(refreshError);
      }
    }

    console.error(`[${new Date().toISOString()}] ❌ [Response Interceptor Error]:`, error);
    return Promise.reject(error);
  }
);

export default axiosInstance;
