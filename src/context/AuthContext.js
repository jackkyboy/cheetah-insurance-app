import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useRef,
  useMemo,
} from "react";
import { jwtDecode } from "jwt-decode";
import { useNavigate, useLocation } from "react-router-dom";
import axiosInstance, {
  getAuthToken,
  getRefreshToken,
  saveAuthToken,
  saveRefreshToken,
  clearTokens,
  refreshAccessToken,
} from "../api/authService";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const hasCheckedTokensRef = useRef(false);
  const hasRedirectedRef = useRef(false);

  const [auth, setAuth] = useState({
    user: null,
    authToken: null,
    refreshToken: null,
    role: null,
    isAdmin: false,
  });

  const [isAuthInitializing, setIsAuthInitializing] = useState(true);

  const isAdminPanel = useMemo(
    () => location.pathname.startsWith("/admin"),
    [location]
  );

  const isTokenExpired = (token) => {
    try {
      const decoded = jwtDecode(token);
      return decoded.exp * 1000 < Date.now();
    } catch {
      return true;
    }
  };

  const setAuthTokenHeaders = (token) => {
    if (token) {
      axiosInstance.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    } else {
      delete axiosInstance.defaults.headers.common["Authorization"];
    }
  };

  const loginUser = (accessToken, refreshToken, role) => {
    localStorage.setItem("authToken", accessToken);
    localStorage.setItem("refreshToken", refreshToken);
    localStorage.setItem("userRole", role);

    const decoded = jwtDecode(accessToken);
    setAuthTokenHeaders(accessToken); // ⚠️ Important
    setAuth({
      user: decoded,
      authToken: accessToken,
      refreshToken,
      role,
      isAdmin: role === "admin",
    });
  };

  const logout = useCallback(() => {
    clearTokens();
    setAuth({
      user: null,
      authToken: null,
      refreshToken: null,
      role: null,
      isAdmin: false,
    });

    if (window.location.pathname !== "/login" && !hasRedirectedRef.current) {
      hasRedirectedRef.current = true;
      setTimeout(() => {
        navigate("/login");
      }, 100);
    }
  }, [navigate]);

  const handleTokenRefresh = useCallback(async () => {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      logout();
      return false;
    }

    try {
      const newAccessToken = await refreshAccessToken();
      if (!newAccessToken) {
        logout();
        return false;
      }

      saveAuthToken(newAccessToken);
      const decoded = jwtDecode(newAccessToken);
      setAuthTokenHeaders(newAccessToken);
      setAuth((prev) => ({
        ...prev,
        user: decoded,
        authToken: newAccessToken,
      }));

      return true;
    } catch {
      logout();
      return false;
    }
  }, [logout]);

  const initializeAuth = useCallback(async () => {
    if (hasCheckedTokensRef.current) return;
    hasCheckedTokensRef.current = true;

    const publicPaths = ["/", "/home", "/login", "/register", "/forgot-password", "/admin/login"];
    const currentPath = window.location.pathname;

    if (publicPaths.some((p) => currentPath.startsWith(p))) {
      setIsAuthInitializing(false);
      return;
    }

    const authToken = getAuthToken();
    const refreshToken = getRefreshToken();

    if (!authToken && !refreshToken) {
      setIsAuthInitializing(false);
      return;
    }

    if (authToken) {
      try {
        const decoded = jwtDecode(authToken);
        if (!isTokenExpired(authToken)) {
          setAuthTokenHeaders(authToken);
          setAuth({
            user: decoded,
            authToken,
            refreshToken,
            role: decoded.role || "user",
            isAdmin: decoded.role === "admin",
          });
          setIsAuthInitializing(false);
          return;
        } else if (refreshToken) {
          const refreshed = await handleTokenRefresh();
          setIsAuthInitializing(!refreshed);
          return;
        } else {
          logout();
        }
      } catch {
        logout();
      }
    }

    setIsAuthInitializing(false);
  }, [handleTokenRefresh, logout]);

  useEffect(() => {
    if (!hasCheckedTokensRef.current) {
      initializeAuth();
    }
  }, [initializeAuth]);

  const isAuthenticated = !!auth.authToken && !isTokenExpired(auth.authToken);

  return (
    <AuthContext.Provider
      value={{
        ...auth,
        isAuthenticated,
        isTokenExpired: isTokenExpired(auth.authToken),
        isAuthInitializing,
        loginUser,
        logout,
      }}
    >
      {!isAuthInitializing && children}
    </AuthContext.Provider>
  );
};

// ✅ Hook สำหรับเรียกใช้
export const useAuth = () => useContext(AuthContext);
