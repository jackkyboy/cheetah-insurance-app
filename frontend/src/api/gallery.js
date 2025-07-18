// /Users/apichet/Downloads/cheetah-insurance-app/src/api/gallery.js

// ✅ /Users/apichet/Downloads/cheetah-insurance-app/src/api/gallery.js

// /src/api/gallery.js
// ✅ /src/api/gallery.js
// ✅ /src/api/gallery.js
import api from "./api";



const normalizeInsuranceType = (type) => {
  const map = {
    "ชั้น 1": "1",
    "1": "1",
    "ชั้น 2+": "2+",
    "2+": "2+",
    "2P": "2P",
    "ชั้น 3+": "3+",
    "3+": "3+",
    "3P": "3P",
    "3": "3",
    "2": "2",
    "0": "0",
  };
  const cleaned = (type || "").trim();
  return map[cleaned] || cleaned;
};

/**
 * ดึงแพ็กเกจประกันภัยจาก backend โดยสามารถส่ง filter + pagination ได้
 * @param {Object} options - ตัวเลือกสำหรับ query
 * @param {string|null} options.brand - ยี่ห้อรถ (เช่น "HONDA")
 * @param {string|null} options.model - รุ่นรถ (เช่น "CIVIC")
 * @param {string|null} options.type - ประเภทประกัน (เช่น "3+")
 * @param {string|null} options.year - ปีรถ (เช่น "2020")
 * @param {string|null} options.company - ชื่อบริษัทประกัน (เช่น "Chubb")
 * @param {number} [options.limit=30] - จำนวนรายการต่อหน้า
 * @param {number} [options.offset=0] - เริ่มจาก index ไหน
 * @returns {Promise<Array>} รายการแพ็กเกจ
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
  
      // ✅ DEBUG: log พารามิเตอร์ที่ถูกส่งจริง
      console.log("📦 fetchGalleryPackages params:", params);
  
      const response = await api.get("/gallery/packages", { params });
      return response.data.results || [];
    } catch (error) {
      console.error("❌ เกิดข้อผิดพลาดในการดึงแพ็กเกจ:", error);
      throw error;
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
      throw error;
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
      throw error;
    }
  };

  