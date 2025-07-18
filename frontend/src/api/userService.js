///Users/apichet/Downloads/cheetah-insurance-app/src/api/userService.js
///Users/apichet/Downloads/cheetah-insurance-app/src/api/userService.js
import apiClient from "./authService";

let cachedUserProfile = null; // Cache for user profile data
let userProfilePromise = null; // For handling multiple simultaneous fetch calls

/**
 * Centralized retry logic with timeout.
 * @param {Function} fn - Function to execute.
 * @param {number} retries - Number of retries.
 * @param {number} timeout - Timeout in milliseconds.
 * @param {string} errorMessage - Error message to throw after retries.
 * @returns {Promise<any>}
 */
const retryWithTimeout = async (fn, retries, timeout, errorMessage) => {
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      return await Promise.race([
        fn(),
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error("Request timed out")), timeout)
        ),
      ]);
    } catch (error) {
      console.warn(`⚠️ Attempt ${attempt}/${retries} failed:`, error.message);
      if (attempt === retries) throw new Error(errorMessage || error.message);
    }
  }
};

/**
 * Handle API errors and retry with token refresh if necessary.
 * @param {Error} error - The API error.
 * @returns {Promise<string>}
 */
const handleApiError = async (error) => {
  if (error.response) {
    const { status, data, config } = error.response;
    console.error("[UserService] API error:", {
      message: data?.message,
      status,
      url: config.url,
      method: config.method,
    });

    if (status === 401) {
      console.warn("[UserService] Unauthorized. Attempting token refresh...");
      try {
        const refreshToken = localStorage.getItem("refreshToken");
        if (!refreshToken) {
          console.warn("[UserService] No refresh token found. Logging out...");
          logoutUser();
          throw new Error("Session expired. Please log in again.");
        }

        const { access_token } = await apiClient.post("/auth/refresh", {
          refresh_token: refreshToken,
        });

        // Save the new token and retry the failed request
        localStorage.setItem("authToken", access_token);
        const retryConfig = {
          ...config,
          headers: { Authorization: `Bearer ${access_token}` },
        };
        const response = await apiClient.request(retryConfig);
        return response.data;
      } catch (refreshError) {
        console.error("[UserService] Token refresh failed. Logging out...");
        logoutUser();
        throw new Error("Session expired. Please log in again.");
      }
    }

    return data?.message || "An error occurred.";
  } else if (error.request) {
    console.error("[UserService] No response from server:", error.request);
    return "No response from the server.";
  } else {
    console.error("[UserService] Unexpected error:", error.message);
    return error.message || "An unexpected error occurred.";
  }
};

/**
 * Fetch user profile with caching, prevention of duplicate calls, retry logic, and timeout.
 * @param {boolean} forceRefresh - If true, forces a fresh fetch from the server.
 * @returns {Promise<Object>} - The user profile data.
 */
export const fetchUserProfile = async (forceRefresh = false) => {
  const RETRY_LIMIT = 3;
  const TIMEOUT_MS = 10000;

  if (!forceRefresh && cachedUserProfile) {
    console.log("✅ Returning cached user profile.");
    return cachedUserProfile;
  }

  if (userProfilePromise && !forceRefresh) {
    console.log("⏳ fetchUserProfile is already in progress. Returning pending promise.");
    return userProfilePromise;
  }

  userProfilePromise = retryWithTimeout(
    async () => {
      console.log("🛠️ Fetching user profile started...");
      const authToken = localStorage.getItem("authToken");
      if (!authToken) throw new Error("No authentication token found. Please log in again.");

      const response = await apiClient.get("/user/profile", {
        headers: { Authorization: `Bearer ${authToken}` },
      });

      if (response?.data) {
        cachedUserProfile = response.data;
        console.log("[UserService] Profile data fetched successfully:", cachedUserProfile);
        return cachedUserProfile;
      } else {
        throw new Error("Invalid response structure from API.");
      }
    },
    RETRY_LIMIT,
    TIMEOUT_MS,
    "Failed to fetch user profile."
  );

  return userProfilePromise.finally(() => {
    userProfilePromise = null;
  });
};

/**
 * Clear cached user profile (e.g., on logout or force refresh).
 */
export const clearUserProfileCache = () => {
  console.log("[UserService] Clearing cached user profile.");
  cachedUserProfile = null;
};

/**
 * Update user profile.
 * @param {Object} profileData - Data to update the profile.
 * @returns {Promise<Object>} - The updated profile data.
 */
export const updateUserProfile = async (profileData) => {
  if (!profileData || typeof profileData !== "object" || Array.isArray(profileData)) {
    throw new Error("[UserService] Invalid payload: Payload must be an object.");
  }

  try {
    console.log("[UserService] Updating user profile with data:", profileData);
    const response = await apiClient.put("/user/profile", profileData, {
      headers: { Authorization: `Bearer ${localStorage.getItem("authToken")}` },
    });

    cachedUserProfile = response.data; // Update cache
    console.log("[UserService] Profile updated successfully:", response.data);
    return response.data;
  } catch (error) {
    const errorMessage = await handleApiError(error);
    console.error("[UserService] Error updating profile:", errorMessage);
    throw new Error(errorMessage);
  }
};

/**
 * Log out the user by clearing tokens and cache, then redirect to login.
 */
export const logoutUser = () => {
  console.warn("[UserService] Logging out user...");
  localStorage.removeItem("authToken");
  localStorage.removeItem("refreshToken");
  clearUserProfileCache();

  if (window.location.pathname !== "/login") {
    console.log("[UserService] Redirecting to login page...");
    window.history.pushState({}, "", "/login");
  }
};
/**
 * Upload profile picture.
 * @param {FormData} formData - FormData containing the profile picture.
 * @returns {Promise<Object>}
 */
export const uploadProfilePicture = async (formData) => {
  if (!(formData instanceof FormData)) {
    throw new Error("[UserService] Invalid payload: FormData required.");
  }

  // ✅ รองรับชื่อทั้ง profile_picture และ file
  const hasValidKey =
    formData.has("profile_picture") || formData.has("file");

  if (!hasValidKey) {
    throw new Error(
      "[UserService] Missing required field: expected 'profile_picture' or 'file'."
    );
  }

  try {
    console.log("[UserService] Uploading profile picture...");
    const response = await apiClient.post("/user/profile-picture", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
        Authorization: `Bearer ${localStorage.getItem("authToken")}`,
      },
    });

    // ✅ อัปเดต cache ถ้ามี
    if (cachedUserProfile?.customer) {
      cachedUserProfile.customer.profile_picture =
        response.data.profile_picture; // ← 🛠 เปลี่ยนตรงนี้เท่านั้น
    }

    console.log(
      "[UserService] Profile picture uploaded successfully:",
      response.data
    );
    return response.data;
  } catch (error) {
    const errorMessage = await handleApiError(error);
    console.error(
      "[UserService] Error uploading profile picture:",
      errorMessage
    );
    throw new Error(errorMessage);
  }
};

