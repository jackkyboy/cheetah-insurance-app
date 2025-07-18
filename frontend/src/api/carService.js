// /Users/apichet/Downloads/cheetah-insurance-app/src/api/carService.js
// /src/api/carService.js
import axiosInstance from "./axios";
import { handleApiRequest } from "./apiUtils";

/**
 * Fetch list of car brands
 */
export const fetchCarBrands = async () => {
  return await handleApiRequest(
    async () => {
      console.log("🚀 Fetching Car Brands...");
      const response = await axiosInstance.get("/multi-step-search/get_brand");
      console.log("✅ Car Brands response:", response.data);

      if (!Array.isArray(response.data)) {
        console.warn("⚠️ Invalid Car Brands data:", response.data);
        return [];
      }
      return response.data;
    },
    "Fetch Car Brands",
    []
  );
};

/**
 * Fetch car models by brand
 * @param {string} carBrand - car brand name
 */
export const fetchCarModels = async (carBrand) => {
  if (!carBrand) throw new Error("Missing required parameter 'carBrand'");

  return await handleApiRequest(
    async () => {
      console.log(`🚀 Fetching Car Models for brand: ${carBrand}`);
      const response = await axiosInstance.get("/multi-step-search/get_model", {
        params: { car_brand: carBrand },
      });
      console.log("✅ Car Models response:", response.data);

      if (!Array.isArray(response.data)) {
        console.warn("⚠️ Invalid Car Models data:", response.data);
        return [];
      }
      return response.data;
    },
    `Fetch Car Models for ${carBrand}`,
    []
  );
};

/**
 * Fetch car submodels by brand and model
 * @param {string} carBrand
 * @param {string} carModel
 */
export const fetchCarSubModels = async (carBrand, carModel) => {
  if (!carBrand || !carModel) throw new Error("Missing required parameters");

  return await handleApiRequest(
    async () => {
      console.log(`🚀 Fetching SubModels for ${carBrand} ${carModel}`);
      const response = await axiosInstance.get("/multi-step-search/get_submodel", {
        params: { car_brand: carBrand, car_model: carModel },
      });
      console.log("✅ Car SubModels response:", response.data);

      if (!Array.isArray(response.data)) {
        console.warn("⚠️ Invalid SubModels data:", response.data);
        return [];
      }
      return response.data;
    },
    `Fetch SubModels for ${carBrand} ${carModel}`,
    []
  );
};

/**
 * Fetch car model years by brand, model, and submodel
 * @param {string} carBrand
 * @param {string} carModel
 * @param {string} carSubModel
 */
export const fetchCarYears = async (carBrand, carModel, carSubModel) => {
  if (!carBrand || !carModel) throw new Error("Missing required parameters");

  return await handleApiRequest(
    async () => {
      console.log(`🚀 Fetching Years for ${carBrand} ${carModel} ${carSubModel}`);
      const response = await axiosInstance.get("/multi-step-search/get_years", {
        params: { car_brand: carBrand, car_model: carModel, car_submodel: carSubModel },
      });
      console.log("✅ Car Years response:", response.data);

      if (!Array.isArray(response.data)) {
        console.warn("⚠️ Invalid Years data:", response.data);
        return [];
      }
      return response.data;
    },
    `Fetch Years for ${carBrand} ${carModel} ${carSubModel}`,
    []
  );
};

/**
 * Fetch list of insurance companies
 */
export const fetchInsuranceCompanies = async () => {
  return await handleApiRequest(
    async () => {
      console.log("🚀 Fetching Insurance Companies...");
      const response = await axiosInstance.get("/car-options/get_insurance_companies");
      console.log("✅ Insurance Companies response:", response.data);

      if (!Array.isArray(response.data)) {
        console.warn("⚠️ Invalid Insurance Companies data:", response.data);
        return [];
      }
      return response.data;
    },
    "Fetch Insurance Companies",
    []
  );
};

/**
 * Fetch CMI packages by filters
 * @param {Object} filters - { carBrand, carModel, carModelYear, insuranceCompany }
 */
export const fetchCMIPackages = async ({ carBrand, carModel, carModelYear, insuranceCompany }) => {
  if (!carBrand || !carModel || !carModelYear || !insuranceCompany) {
    throw new Error("Missing parameters for CMI packages");
  }

  return await handleApiRequest(
    async () => {
      console.log("🚀 Fetching CMI Packages...");
      const response = await axiosInstance.post("/multi-step-search/fetch_packages", {
        car_brand: carBrand,
        car_model: carModel,
        car_model_year: carModelYear,
        insurance_company: insuranceCompany,
        is_cmi: true,
      });
      console.log("✅ CMI Packages response:", response.data);

      if (!Array.isArray(response.data)) {
        console.warn("⚠️ Invalid CMI Packages data:", response.data);
        return [];
      }
      return response.data;
    },
    "Fetch CMI Packages",
    []
  );
};

/**
 * Fetch fallback suggestions when no data found
 * @param {string} carBrand
 * @param {string} carModel
 */
export const fetchFallbackSuggestions = async (carBrand, carModel) => {
  if (!carBrand || !carModel) throw new Error("Missing parameters for fallback suggestions");

  return await handleApiRequest(
    async () => {
      console.log("🔍 Fetching fallback suggestions...");
      const response = await axiosInstance.get("/multi-step-search/fallback_suggestions", {
        params: { car_brand: carBrand, car_model: carModel },
      });
      console.log("✅ Fallback Suggestions response:", response.data);

      if (!response.data || typeof response.data !== "object") {
        console.warn("⚠️ Invalid fallback suggestions data:", response.data);
        return {
          available_years: [],
          available_insurance_types: [],
          similar_companies: [],
        };
      }
      return response.data;
    },
    "Fetch Fallback Suggestions",
    {
      available_years: [],
      available_insurance_types: [],
      similar_companies: [],
    }
  );
};
