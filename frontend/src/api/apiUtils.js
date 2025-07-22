// /src/utils/apiUtils.js
// ⛳️ แทรกด้านบน
import axios from "../api/axios";
/**
 * Utility functions for API requests and error handling
 */

const BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:5000";

/**
 * Handle API Request with enhanced error handling, array support, and better logging.
 *
 * @param {Function} requestFn - Function that executes the API request.
 * @param {string} context - Description of the request for logging.
 * @param {*} fallback - Fallback value to return in case of an error.
 * @returns {Promise<*>} - API response data or fallback value.
 */
export const handleApiRequest = async (requestFn, context = "API Request", fallback = null) => {
  try {
    console.log(`🚀 [${context}] Sending request...`);
    const response = await requestFn();

    // เช็ค response ว่าเป็น object และมี data
    if (!response || typeof response !== "object") {
      console.warn(`⚠️ [${context}] API responded with an invalid response.`);
      return fallback;
    }

    // axios response headers อาจเป็น AxiosHeaders หรือ Object
    let contentType = "Unknown";
    if (response.headers) {
      if (typeof response.headers.get === "function") {
        // กรณี fetch-like headers
        contentType = response.headers.get("content-type") || "Unknown";
      } else if (typeof response.headers["content-type"] === "string") {
        // กรณี axios headers object
        contentType = response.headers["content-type"];
      }
    }

    const metadata = {
      status: response.status ?? "Unknown",
      statusText: response.statusText ?? "Unknown",
      contentType,
    };
    console.log(`📡 [${context}] Response Metadata:`, metadata);

    if (response.status === 404) {
      console.warn(`⚠️ [${context}] Resource not found (404). Returning fallback.`);
      return fallback;
    }

    if (!response.data) {
      console.warn(`⚠️ [${context}] API responded with an empty structure.`);
      return fallback;
    }

    // คืนค่าเฉพาะ data ที่เป็น payload จริง
    return response.data;
  } catch (error) {
    console.error(`❌ [${context}] API Error:`, error);

    if (error.response) {
      console.warn(`⚠️ [${context}] API Error Response:`, {
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data,
      });
    }

    return fallback;
  }
};



/**
 * Universal API fetcher with automatic fallback for failed requests.
 *
 * @param {string} endpoint - API endpoint (relative to BASE_URL).
 * @param {Object} [options={}] - Fetch options (method, headers, body).
 * @param {*} [fallback=null] - Value to return if the API call fails.
 * @returns {Promise<*>} - API response data or fallback value.
 */
  export const fetchWithFallback = async (endpoint, options = {}, fallback = null) => {
    try {
      console.log(`🚀 [API] Fetching ${endpoint} ...`);

      const res = await axios.request({
        url: endpoint,
        method: options.method || "get",
        headers: options.headers || {},
        data: options.body || undefined, // use `data` for axios body
      });

      const data = res.data;

      if (!data || typeof data !== "object") {
        console.warn(`⚠️ [API] Invalid response from ${endpoint}:`, data);
        return fallback;
      }

      console.log(`✅ [API] Fetched successfully from ${endpoint}:`, data);
      return data;
    } catch (error) {
      console.error(`❌ [API] Error fetching ${endpoint}:`, error.message);
      return fallback;
    }
  };



/**
 * Sanitize a logo URL by appending the base URL if necessary.
 *
 * @param {string} url - The URL of the logo.
 * @returns {string} - Sanitized URL with the full path.
 */
export const sanitizeLogoUrl = (url) => {
  if (!url || url.includes("default-logo.svg")) {
    return `${BASE_URL}/logos/default-logo.svg`;
  }
  return url.startsWith("http") ? url : `${BASE_URL}${url}`;
};

/**
 * Validate API response structure.
 *
 * @param {Object} response - The API response.
 * @param {Array<string>} requiredKeys - List of required keys in the response.
 * @returns {boolean} - True if the response is valid, false otherwise.
 */
export const validateApiResponse = (response, requiredKeys = []) => {
  if (!response || typeof response !== "object") {
    console.error("[validateApiResponse] Invalid response structure:", response);
    return false;
  }

  for (const key of requiredKeys) {
    if (!(key in response)) {
      console.error(`[validateApiResponse] Missing key: ${key} in response`, response);
      return false;
    }
  }

  return true;
};

/**
 * Handle API error with logging.
 *
 * @param {Object} error - The error object.
 * @param {string} context - Context or description of the API call.
 * @returns {null} - Always returns null to indicate error was handled.
 */
export const handleApiError = (error, context = "API") => {
  if (error.response) {
    console.error(`🌐 [${context}] Server responded with status ${error.response.status}:`, error.response.data);
  } else if (error.request) {
    console.error(`🚫 [${context}] No response received from server:`, error.request);
  } else {
    console.error(`⚙️ [${context}] Error in request setup:`, error.message);
  }
  return null;
};

/**
 * Paginate API results.
 *
 * @param {Array} results - Array of results to paginate.
 * @param {number} page - The current page number.
 * @param {number} itemsPerPage - Number of items per page.
 * @returns {Array} - Paginated array of results.
 */
export const paginateResults = (results = [], page = 1, itemsPerPage = 10) => {
  return results.slice((page - 1) * itemsPerPage, page * itemsPerPage);
};

/**
 * Convert query parameters object to a URL-encoded string.
 *
 * @param {Object} params - Object containing query parameters.
 * @returns {string} - URL-encoded query string.
 */
export const buildQueryParams = (params = {}) => {
  return new URLSearchParams(params).toString();
};

/**
 * Parse response and extract results.
 *
 * @param {Object} response - API response.
 * @param {string} resultsKey - Key containing the results array in the response.
 * @returns {Array} - Extracted results array or empty array if invalid.
 */
export const extractResults = (response, resultsKey = "results") => {
  if (!response || !response[resultsKey] || !Array.isArray(response[resultsKey])) {
    console.warn("[extractResults] Invalid or missing results in response:", response);
    return [];
  }
  return response[resultsKey];
};

/**
 * Retry an API request with exponential backoff.
 *
 * @param {Function} requestFn - Function to execute the API request.
 * @param {number} retries - Number of retries.
 * @param {number} delay - Initial delay in milliseconds.
 * @returns {Promise<*>} - API response or null if all retries fail.
 */
export const retryRequest = async (requestFn, retries = 3, delay = 1000) => {
  let attempt = 0;
  while (attempt < retries) {
    try {
      const response = await requestFn();
      return response;
    } catch (error) {
      attempt++;
      if (error.response?.status === 401) {
        console.warn("🚫 [retryRequest] Unauthorized. Redirecting to login.");
        window.location.href = "/login";
        return null;
      }

      if (attempt >= retries) {
        console.error("❌ [retryRequest] All retries failed.");
        throw error;
      }

      console.warn(`🔄 Retry attempt ${attempt}/${retries}. Waiting ${delay}ms...`);
      await new Promise((resolve) => setTimeout(resolve, delay));
      delay *= 2; // Exponential backoff
    }
  }
};

export default {
  handleApiRequest,
  fetchWithFallback,
  sanitizeLogoUrl,
  validateApiResponse,
  handleApiError,
  paginateResults,
  buildQueryParams,
  extractResults,
  retryRequest,
};
