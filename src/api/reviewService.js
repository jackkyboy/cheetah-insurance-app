// /Users/apichet/Downloads/cheetah-insurance-app/src/api/reviewService.js
// 📍 /src/api/reviewService.js
// 📍 /src/api/reviewService.js
import apiClient from "./authService"; // ✅ interceptor แนบ token อัตโนมัติ

/**
 * Submit a new review for an insurance company.
 * @param {Object} reviewData
 * @param {number} reviewData.company_id - Required
 * @param {number} reviewData.package_id - Required
 * @param {number} reviewData.rating - Required (1–5)
 * @param {string} [reviewData.comment]
 * @returns {Promise<Object>}
 */
export const submitReview = async (reviewData) => {
  const { company_id, package_id, rating, comment } = reviewData;

  if (!company_id || !package_id || typeof rating !== "number") {
    throw { error: "กรุณากรอกข้อมูลให้ครบ: company_id, package_id, และ rating" };
  }

  try {
    console.log("[ReviewService] Submitting review:", reviewData);
    const response = await apiClient.post("/reviews/", {
      company_id,
      package_id,
      rating,
      comment: comment || "",
    });
    console.log("[ReviewService] ✅ Review submitted:", response.data);
    return response.data;
  } catch (error) {
    console.error("[ReviewService] ❌ Error submitting review:", error);
    throw error.response?.data || { error: "เกิดข้อผิดพลาดขณะส่งรีวิว" };
  }
};

/**
 * Fetch reviews for a specific package.
 * @param {number} packageId
 * @returns {Promise<Array>}
 */
export const getReviewsForPackage = async (packageId) => {
  try {
    console.log(`[ReviewService] Fetching reviews for package ID: ${packageId}`);
    const response = await apiClient.get(`/reviews/package/${packageId}`);
    return response.data.reviews;
  } catch (error) {
    console.error("[ReviewService] Error fetching reviews:", error);
    throw error.response?.data || { error: "เกิดข้อผิดพลาดในการโหลดรีวิว" };
  }
};

/**
 * Fetch reviews by the current logged-in customer.
 * @returns {Promise<Array>}
 */
export const getReviewsByCustomer = async () => {
  try {
    const response = await apiClient.get("/reviews/customer");
    return response.data.reviews;
  } catch (error) {
    console.error("[ReviewService] Error fetching customer reviews:", error);
    throw error.response?.data || { error: "ไม่สามารถโหลดรีวิวของคุณได้" };
  }
};

/**
 * Fetch average ratings across all companies.
 * @returns {Promise<Object>}
 */
export const getInsuranceReviewSummary = async () => {
  try {
    const response = await apiClient.get("/reviews/average-ratings");
    return response.data;
  } catch (error) {
    console.error("[ReviewService] Error fetching insurance review summary:", error);
    throw error.response?.data || { error: "ไม่สามารถโหลดสรุปคะแนนได้" };
  }
};
