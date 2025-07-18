// /Users/apichet/Downloads/cheetah-insurance-app/src/api/multiStepSearchService.js
// ✅ Import ที่ถูกต้อง
// ✅ Import ที่ถูกต้อง
import axiosInstance from "./axiosInstance"; // ✅ ใช้ axiosInstance ที่ pre-configured
import { handleApiRequest } from "./apiUtils"; // ✅ Import Utility function

const BASE_URL = `${process.env.REACT_APP_API_BASE_URL}/multi-step-search`;


/**
 * ✅ Fetch car brands
 */
export const fetchCarBrands = async () => {
  return await handleApiRequest(
    () => axiosInstance.get(`${BASE_URL}/get_brand`),
    "Fetch Car Brands",
    []
  );
};

/**
 * ✅ Fetch car models by brand
 */
export const fetchCarModels = async (carBrand) => {
  if (!carBrand) {
    console.error("❌ fetchCarModels: Missing required parameter `carBrand`.");
    throw new Error("Car brand is required.");
  }

  return await handleApiRequest(
    () =>
      axiosInstance.get(`${BASE_URL}/get_model`, {
        params: { car_brand: carBrand },
      }),
    `Fetch Car Models for Brand: ${carBrand}`,
    []
  );
};

/**
 * ✅ Fetch submodels by brand and model
 */
export const fetchCarSubModels = async (carBrand, carModel) => {
  if (!carBrand || !carModel) {
    console.error("❌ fetchCarSubModels: Missing required parameters `carBrand` or `carModel`.");
    throw new Error("Both car brand and car model are required.");
  }

  return await handleApiRequest(
    () =>
      axiosInstance.get(`${BASE_URL}/get_submodel`, {
        params: { car_brand: carBrand, car_model: carModel },
      }),
    `Fetch Car SubModels for Brand: ${carBrand}, Model: ${carModel}`,
    []
  );
};

/**
 * ✅ Fetch car model years
 */
export const fetchCarModelYears = async (carBrand, carModel) => {
  if (!carBrand || !carModel) {
    console.error("❌ fetchCarModelYears: Missing required parameters `carBrand` or `carModel`.");
    return [];
  }

  try {
    console.log(`🔍 Fetching car model years for brand: ${carBrand}, model: ${carModel}`);

    const response = await axiosInstance.get(`${BASE_URL}/get_years`, {
      params: { car_brand: carBrand, car_model: carModel },
    });

    if (!response?.data || typeof response.data !== "object") {
      console.error("❌ fetchCarModelYears: Invalid API response format.", response);
      return [];
    }

    const { car_model_years } = response.data;

    if (!Array.isArray(car_model_years)) {
      console.error("❌ fetchCarModelYears: `car_model_years` is not an array.", car_model_years);
      return [];
    }

    const filteredYears = car_model_years
      .filter((year) => year && String(year).trim() !== "" && !isNaN(year))
      .map((year) => String(year).trim());

    console.log("✅ Cleaned Car Model Years:", filteredYears);

    return filteredYears.length ? filteredYears : [];
  } catch (error) {
    console.error("❌ fetchCarModelYears Error:", error);
    return [];
  }
};

/**
 * ✅ Fetch repair types
 */
export const fetchRepairTypes = async () => {
  console.log("🚀 [fetchRepairTypes] Calling API...");

  // ให้ handleApiRequest รับฟังก์ชันที่ return axios call ตรงๆ
  return await handleApiRequest(
    () => axiosInstance.get(`${BASE_URL}/get_repair_types`),
    "Fetch Repair Types",
    ["ซ่อมอู่", "ซ่อมห้าง"]
  ).then((data) => {
    // data คือ response.data ที่ถูก return จาก handleApiRequest
    if (data && Array.isArray(data.repair_types) && data.repair_types.length > 0) {
      console.log("✅ [Fetch Repair Types] Valid Repair Types:", data.repair_types);
      return data.repair_types;
    }

    console.warn("⚠️ [Fetch Repair Types] API responded with an empty or invalid structure.");
    return ["ซ่อมอู่", "ซ่อมห้าง"];
  });
};



/**
 * ✅ Fetch insurance types
 */
export const fetchInsuranceTypes = async () => {
  console.log("🚀 [fetchInsuranceTypes] Calling API...");

  const data = await handleApiRequest(
    async () => {
      const response = await axiosInstance.get(`${BASE_URL}/get_insurance_types`);

      console.log("✅ [fetchInsuranceTypes] Raw API Response:", response);

      if (!response?.data || typeof response.data !== "object") {
        console.warn("⚠️ [fetchInsuranceTypes] API response is missing or not an object:", response?.data);
        return ["1", "2", "2+", "3", "3+"];
      }

      const { insurance_types } = response.data;

      if (Array.isArray(insurance_types) && insurance_types.length > 0) {
        console.log("✅ [fetchInsuranceTypes] Extracted insurance_types:", insurance_types);
        return insurance_types;
      }

      console.warn("⚠️ [fetchInsuranceTypes] Unexpected or empty data structure, using fallback:", response.data);
      return ["1", "2", "2+", "3", "3+"];
    },
    "Fetch Insurance Types",
    ["1", "2", "2+", "3", "3+"]
  );

  console.log("✅ [fetchInsuranceTypes] Final Insurance Types:", data);
  return data;
};


/**
 * ✅ Fetch insurance packages
 */
export const fetchPackages = async (filters) => {
  try {
    console.log("📤 Fetching insurance packages with filters:", filters);

    const response = await axiosInstance.post(`${BASE_URL}/fetch_packages`, filters);

    if (!response?.data || typeof response.data !== "object") {
      console.error("❌ fetchPackages: Invalid API response format.", response);
      return [];
    }

    console.log("📥 Full API Response:", response.data);

    if (!Array.isArray(response.data.results)) {
      console.error("❌ fetchPackages: `results` is missing or not an array.", response.data);
      return [];
    }

    console.log("✅ API Response: Found", response.data.results.length, "packages.");
    return response.data.results ?? [];
  } catch (error) {
    console.error("❌ fetchPackages Error:", error.response?.data || error.message);
    return [];
  }
};


/**
 * ✅ Fetch available insurance & repair options dynamically
 * Used after brand/model/submodel/year selected
 */
export const fetchAvailableOptions = async (filters) => {
  try {
    console.log("🚀 [fetchAvailableOptions] Sending filters:", filters);

    const data = await handleApiRequest(
      () => axiosInstance.get(`${BASE_URL}/available-options`, { params: filters }),
      "Fetch Available Options",
      { insurance_types: [], repair_types: [], years: [] }
    );

    console.log("✅ [fetchAvailableOptions] Matched Options:", data);
    return data;
  } catch (error) {
    console.error("❌ fetchAvailableOptions Error:", error);
    return { insurance_types: [], repair_types: [], years: [] };
  }
};
