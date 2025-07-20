// /Users/apichet/Downloads/cheetah-insurance-app/src/api/gallery.js

// ✅ /Users/apichet/Downloads/cheetah-insurance-app/src/api/gallery.js

import api from "./api";

const normalizeInsuranceType = (type) => {
  const map = {
    "ชั้น 1": "1", "1": "1",
    "ชั้น 2+": "2+", "2+": "2+", "2P": "2P",
    "ชั้น 3+": "3+", "3+": "3+", "3P": "3P",
    "3": "3", "2": "2", "0": "0",
  };
  const cleaned = (type || "").trim();
  return map[cleaned] || cleaned;
};

/**
 * ดึงแพ็กเกจประกันภัยจาก backend โดยสามารถส่ง filter + pagination ได้
 */
export const fetchGalleryPackages = async ({
  brand = null,
  model = null,
  type = null,
  year = null,
  company = null,
  limit = 30,
  offset = 0,
} = {}) => {
  try {
    const params = { limit, offset };
    if (brand) params.brand = brand.trim();
    if (model) params.model = model.trim();
    if (type) params.type = normalizeInsuranceType(type);
    if (year) params.year = year;
    if (company) params.company = company.trim();

    console.log("📦 fetchGalleryPackages params:", params);

    const response = await api.get("/gallery/packages", { params });

    const res = response.data;
    return Array.isArray(res) ? res : res.results || [];
  } catch (error) {
    console.error("❌ เกิดข้อผิดพลาดในการดึงแพ็กเกจ:", error);
    return [];
  }
};

/**
 * ดึงรุ่นรถทั้งหมดของยี่ห้อที่เลือก
 */
export const fetchCarModels = async (brand) => {
  try {
    const response = await api.get("/gallery/car-models", {
      params: { brand: brand.trim() },
    });
    return response.data.models || [];
  } catch (error) {
    console.error("❌ เกิดข้อผิดพลาดในการดึงรุ่นรถ:", error);
    return [];
  }
};

/**
 * ดึงปีรถที่มีจริงของรุ่นที่เลือก
 */
export const fetchModelYears = async (brand, model) => {
  try {
    const response = await api.get("/gallery/model-years", {
      params: { brand: brand.trim(), model: model.trim() },
    });
    return response.data.years || [];
  } catch (error) {
    console.error("❌ เกิดข้อผิดพลาดในการดึงปีรถ:", error);
    return [];
  }
};
