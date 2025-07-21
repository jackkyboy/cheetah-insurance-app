/* /Users/apichet/Downloads/cheetah-insurance-app/src/api/authService.js */
import axios from "axios";
import { jwtDecode } from "jwt-decode";
import { saveAdminAuthToken, saveAdminRefreshToken } from "./adminAuthService";

const BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:5000/api";

// 👉 ปิด log นี้เมื่อ production
if (process.env.NODE_ENV !== "production") {
  console.log("🚀 Using API BASE URL:", BASE_URL);
}

const AUTH_TOKEN_KEY = "authToken";
const REFRESH_TOKEN_KEY = "refreshToken";
const USER_ROLE_KEY = "userRole";

// 🔐 Token management
export const getAuthToken = () => localStorage.getItem(AUTH_TOKEN_KEY);
export const getRefreshToken = () => localStorage.getItem(REFRESH_TOKEN_KEY);
export const getUserRole = () => localStorage.getItem(USER_ROLE_KEY);

export const saveAuthToken = (token) => {
  if (token) {
    const decoded = jwtDecode(token);
    const role = decoded?.role || "user";
    if (role === "admin") saveAdminAuthToken(token);
    else localStorage.setItem(AUTH_TOKEN_KEY, token);
  }
};

export const saveRefreshToken = (token) => {
  if (token) {
    const decoded = jwtDecode(token);
    const role = decoded?.role || "user";
    if (role === "admin") saveAdminRefreshToken(token);
    else localStorage.setItem(REFRESH_TOKEN_KEY, token);
  }
};

export const saveUserRole = (role) => {
  if (role) localStorage.setItem(USER_ROLE_KEY, role);
};

export const clearTokens = () => {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_ROLE_KEY);
  window.location.href = "/login";
};

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
});

export const refreshAccessToken = async () => {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  try {
    const res = await axios.post(`${BASE_URL}/auth/refresh`, { refresh_token: refreshToken });
    const { access_token, refresh_token } = res.data || {};

    if (!access_token) return null;

    saveAuthToken(access_token);
    saveRefreshToken(refresh_token || refreshToken);
    return access_token;
  } catch (err) {
    return null;
  }
};

// Interceptors
let isRefreshing = false;
let refreshSubscribers = [];

const onRefreshed = (token) => {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
};

apiClient.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (err) => Promise.reject(err)
);

apiClient.interceptors.response.use(
  (res) => res,
  async (err) => {
    const originalRequest = err.config;

    if (err.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (isRefreshing) {
        return new Promise((resolve) => {
          refreshSubscribers.push((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            resolve(apiClient(originalRequest));
          });
        });
      }

      isRefreshing = true;
      const newToken = await refreshAccessToken();
      isRefreshing = false;

      if (!newToken) {
        clearTokens();
        return Promise.reject(err);
      }

      saveAuthToken(newToken);
      onRefreshed(newToken);
      originalRequest.headers.Authorization = `Bearer ${newToken}`;
      return apiClient(originalRequest);
    }

    return Promise.reject(err);
  }
);

// 🔐 Auth functions
export const login = async (email, password) => {
  const res = await apiClient.post(`/auth/login`, { email, password });
  const { access_token, refresh_token, user } = res.data;

  if (!access_token || !refresh_token || !user?.role) {
    throw new Error("Invalid login response.");
  }

  saveAuthToken(access_token);
  saveRefreshToken(refresh_token);
  saveUserRole(user.role);

  return { access_token, refresh_token, role: user.role };
};

export const logout = () => clearTokens();

export const fetchAuthenticatedUser = async () => {
  const { data } = await apiClient.get(`/user/profile`);
  return data;
};

export const register = async (userData) => {
  const { data } = await apiClient.post(`/auth/register`, userData);
  return data;
};

export const requestPasswordReset = async (email) => {
  const { data } = await apiClient.post(`/auth/forgot-password`, { email });
  return data;
};

export const resetPassword = async (token, newPassword) => {
  const { data } = await apiClient.post(`/auth/reset-password`, { token, new_password: newPassword });
  return data;
};

export default apiClient;
