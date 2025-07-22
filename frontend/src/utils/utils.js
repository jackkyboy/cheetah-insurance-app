// /Users/apichet/Downloads/cheetah-insurance-app/src/utils/utils.js


// /Users/apichet/Downloads/cheetah-insurance-app/src/utils/utils.js
/**
 * Sanitize logo URL.
 * Converts a relative logo path to a full URL or returns a default logo if none is provided.
 *
 * @param {string} logoUrl - The original logo URL or path.
 * @returns {string} The sanitized full logo URL.
 */
export const sanitizeLogoUrl = (logoUrl) => {
  const defaultLogo = `${process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:5000"}/logos/default-logo.svg`;

  try {
    console.log(`🔍 [sanitizeLogoUrl] Input logo URL: "${logoUrl}"`);

    // Check if logoUrl is invalid or refers to the default logo
    if (!logoUrl || typeof logoUrl !== "string" || logoUrl.trim() === "" || logoUrl.includes("default-logo.svg")) {
      console.warn(`⚠️ [sanitizeLogoUrl] Invalid logo URL. Using default: "${defaultLogo}"`);
      return defaultLogo;
    }

    // If logoUrl is a full URL
    if (logoUrl.startsWith("http://") || logoUrl.startsWith("https://")) {
      console.log(`✅ [sanitizeLogoUrl] Full URL detected: "${logoUrl}"`);
      return logoUrl;
    }

    // If logoUrl is a relative path
    if (logoUrl.startsWith("/")) {
      const fullUrl = `${process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:5000"}${logoUrl}`;
      console.log(`✅ [sanitizeLogoUrl] Relative path detected. Full URL constructed: "${fullUrl}"`);
      return fullUrl;
    }

    // If no valid format is found, fallback to default
    console.warn(`⚠️ [sanitizeLogoUrl] Unknown logo format. Using default: "${defaultLogo}"`);
    return defaultLogo;
  } catch (error) {
    console.error(`❌ [sanitizeLogoUrl] Error processing URL: "${error.message}". Using fallback: "${defaultLogo}"`);
    return defaultLogo;
  }
};

/**
 * Sanitize a URL to ensure it is properly formatted.
 *
 * @param {string} url - The URL to sanitize.
 * @returns {string} - The sanitized URL.
 */
export const sanitizeUrl = (url) => {
  try {
    console.log(`🔍 [sanitizeUrl] Input URL: "${url}"`);

    if (!url || typeof url !== "string") {
      console.warn("⚠️ [sanitizeUrl] Invalid URL provided. Returning empty string.");
      return "";
    }

    // Normalize URL by removing extra slashes and fixing protocol
    const sanitizedUrl = url.replace(/\/+/g, "/").replace(":/", "://");
    console.log(`✅ [sanitizeUrl] Sanitized URL: "${sanitizedUrl}"`);
    return sanitizedUrl;
  } catch (error) {
    console.error(`❌ [sanitizeUrl] Error sanitizing URL: "${error.message}".`);
    return url || "";
  }
};

/**
 * Add query parameters to a URL.
 *
 * @param {string} url - The base URL.
 * @param {object} params - An object representing query parameters.
 * @returns {string} - The URL with query parameters appended.
 */
export const addQueryParams = (url, params) => {
  try {
    console.log(`🔍 [addQueryParams] Input URL: "${url}", Params:`, params);

    if (!url || typeof url !== "string") {
      console.warn("⚠️ [addQueryParams] Invalid URL provided. Returning empty string.");
      return "";
    }

    const query = new URLSearchParams(params).toString();
    const separator = url.includes("?") ? "&" : "?";
    const fullUrl = `${url}${separator}${query}`;
    console.log(`✅ [addQueryParams] URL with query params: "${fullUrl}"`);
    return fullUrl;
  } catch (error) {
    console.error(`❌ [addQueryParams] Error adding query params: "${error.message}".`);
    return url;
  }
};


