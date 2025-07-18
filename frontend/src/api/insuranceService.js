/*/Users/apichet/Downloads/cheetah-insurance-app/src/api/insuranceService.js */
// ✅ Import ที่ถูกต้อง
// /src/api/insuranceService.js
import axiosInstance from "./axiosInstance";
import { handleApiRequest } from "./apiUtils";

const DEBUG_MODE = process.env.REACT_APP_DEBUG === "true";
const requiredFields = ["car_brand", "car_model", "car_model_year"];

const defaultPayload = {
  car_brand: null,
  car_model: null,
  car_model_year: null,
  insurance_type: "1",
};

/**
 * Fetch insurance packages with required filters
 * @param {Object} payload - Filter data (car_brand, car_model, car_model_year, insurance_type)
 */
export const fetchInsurancePackages = async (payload) => {
  const finalPayload = { ...defaultPayload, ...payload };
  const missingFields = requiredFields.filter((field) => !finalPayload[field]);

  if (missingFields.length > 0) {
    throw new Error(`Missing required fields: ${missingFields.join(", ")}`);
  }

  if (DEBUG_MODE) {
    console.log("[fetchInsurancePackages] Payload:", finalPayload);
  }

  return await handleApiRequest(
    () => axiosInstance.post("/bigquery/query", finalPayload),
    "Fetch Insurance Packages",
    { results: [] }
  );
};

/**
 * Prepare insurance info before saving or further processing
 * @param {Object} data - Insurance info payload
 */
export const prepareInsuranceInfo = async (data) => {
  return await handleApiRequest(
    () => axiosInstance.post("/insurance/prepare-info", data),
    "Prepare Insurance Info"
  );
};

/**
 * Fetch insurance info by customer ID
 * @param {string} customerId - Customer identifier
 */
export const fetchInsuranceInfo = async (customerId) => {
  if (!customerId) throw new Error("Customer ID is required.");

  return await handleApiRequest(
    () => axiosInstance.get(`/insurance/info/${customerId}`),
    "Fetch Insurance Info"
  );
};

/**
 * Save insurance info to backend
 * @param {Object} insuranceData - Data to save
 */
export const saveInsuranceInfo = async (insuranceData) => {
  return await handleApiRequest(
    () => axiosInstance.post("/insurance/save", insuranceData),
    "Save Insurance Info"
  );
};

/**
 * Save insurance preparation data
 * @param {Object} payload - Preparation data
 */
export const saveInsurancePreparation = async (payload) => {
  return await handleApiRequest(
    () => axiosInstance.post("/insurance/preparation", payload),
    "Save Insurance Preparation"
  );
};

/**
 * Get insurance preparation data by user ID
 * @param {string} userId - User identifier
 */
export const getInsurancePreparation = async (userId) => {
  if (!userId) throw new Error("User ID is required.");

  return await handleApiRequest(
    () => axiosInstance.get(`/insurance-preparation/${userId}`),
    "Get Insurance Preparation"
  );
};

/**
 * Update insurance preparation data by preparation ID
 * @param {string} preparationId - Preparation record ID
 * @param {Object} updates - Fields to update
 */
export const updateInsurancePreparation = async (preparationId, updates) => {
  return await handleApiRequest(
    () => axiosInstance.put(`/insurance-preparation/${preparationId}`, updates),
    "Update Insurance Preparation"
  );
};

/**
 * Delete insurance preparation by preparation ID
 * @param {string} preparationId - Preparation record ID
 */
export const deleteInsurancePreparation = async (preparationId) => {
  return await handleApiRequest(
    () => axiosInstance.delete(`/insurance-preparation/${preparationId}`),
    "Delete Insurance Preparation"
  );
};
