// /Users/apichet/Downloads/cheetah-insurance-app/frontend/src/utils/imageUtils.js
// /src/utils/imageUtils.js

/**
 * Resolve a profile image URL, falling back to default image if needed.
 * Handles absolute URLs, relative paths, and empty/null cases.
 *
 * @param {string|null} path - The relative or absolute path to the image.
 * @returns {string} - A full image URL ready for use in <img src=...>
 */
export const resolveProfileImage = (path) => {
    const DEFAULT_IMAGE = "/images/default-profile.png?v=1";
  
    if (!path || typeof path !== "string" || path.trim() === "") {
      return DEFAULT_IMAGE;
    }
  
    if (path.startsWith("http://") || path.startsWith("https://")) {
      return path;
    }
  
    const base = process.env.REACT_APP_API_BASE_URL || window.location.origin;
    return `${base}${path.startsWith("/") ? path : `/${path}`}`;
  };
  