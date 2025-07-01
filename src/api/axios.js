/*/Users/apichet/Downloads/cheetah-insurance-app/src/api/axios.js*/
import axios from "axios";

// 🔧 Base URL
const BASE_URL = process.env.REACT_APP_API_BASE_URL?.replace(/\/+$/, "") || "http://127.0.0.1:5000";
const DEBUG_MODE = process.env.REACT_APP_DEBUG === "true";

// ✅ Axios instance
const axiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

// ✅ Admin token utils
const getAdminAuthToken = () => sessionStorage.getItem("adminAuthToken") || localStorage.getItem("adminAuthToken");
const getAdminRefreshToken = () => sessionStorage.getItem("adminRefreshToken") || localStorage.getItem("adminRefreshToken");
const setAdminAuthToken = (token) => {
  sessionStorage.setItem("adminAuthToken", token);
  localStorage.setItem("adminAuthToken", token);
};

// ✅ User token utils
const getUserAuthToken = () => sessionStorage.getItem("token") || localStorage.getItem("token");

let isLoggingOut = false;
const clearAdminTokensAndLogout = () => {
  if (!isLoggingOut) {
    isLoggingOut = true;
    console.warn("🛑 Logging out Admin...");
    localStorage.removeItem("adminAuthToken");
    localStorage.removeItem("adminRefreshToken");
    sessionStorage.removeItem("adminAuthToken");
    sessionStorage.removeItem("adminRefreshToken");
    window.location.href = "/admin/login";
  }
};

// ✅ Attach Authorization token in request
axiosInstance.interceptors.request.use(
  (config) => {
    const adminToken = getAdminAuthToken();
    const userToken = getUserAuthToken();

    const tokenToUse = adminToken || userToken;

    if (tokenToUse) {
      config.headers["Authorization"] = `Bearer ${tokenToUse}`;
      if (DEBUG_MODE) console.log("🔐 Attaching token:", tokenToUse);
    } else {
      if (DEBUG_MODE) console.warn("⚠️ No token attached to request");
    }

    return config;
  },
  (error) => {
    console.error("❌ Request error:", error);
    return Promise.reject(error);
  }
);

let isRefreshing = false;
let failedRequestsQueue = [];

const processQueue = (error, token = null) => {
  failedRequestsQueue.forEach((prom) => {
    if (token) prom.resolve(token);
    else prom.reject(error);
  });
  failedRequestsQueue = [];
};

// ✅ Response interceptor with admin token refresh logic
axiosInstance.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = getAdminRefreshToken();

      if (!refreshToken) {
        clearAdminTokensAndLogout();
        return Promise.reject(error);
      }

      originalRequest._retry = true;

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedRequestsQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers["Authorization"] = `Bearer ${token}`;
            return axiosInstance(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      isRefreshing = true;

      try {
        const res = await axios.post(`${BASE_URL}/api/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token } = res.data;
        if (!access_token) throw new Error("No access token returned");

        setAdminAuthToken(access_token);
        processQueue(null, access_token);

        originalRequest.headers["Authorization"] = `Bearer ${access_token}`;
        return axiosInstance(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        clearAdminTokensAndLogout();
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default axiosInstance;
