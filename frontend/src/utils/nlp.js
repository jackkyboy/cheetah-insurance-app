// /Users/apichet/Downloads/cheetah-insurance-app/src/utils/nlp.js
// 📁 /src/utils/nlp.js
import rawBrands from "../data/car_brands.json";
import rawSubmodels from "../data/car_submodels.json";

// 🔧 Normalize submodels เป็น { HONDA: ["2WD", "CIVIC", "ACCORD", ...] }
const carSubmodels = rawSubmodels.reduce((acc, item) => {
  const brand = item.car_brand?.toUpperCase();
  if (!acc[brand]) acc[brand] = [];
  acc[brand].push(item.car_submodel?.toUpperCase());
  return acc;
}, {});

// 🔧 Extract brand names
const carBrands = rawBrands.map((b) => b.car_brand?.toUpperCase());

export const parseInsuranceQuery = (text = "") => {
  const lower = text.toLowerCase().replace(/\s+/g, " ").trim();

  // ✅ ตรวจจับแบรนด์
  const matchedBrand = carBrands.find((brand) =>
    lower.includes(brand.toLowerCase())
  );
  const brand = matchedBrand ?? null;

  // ✅ ตรวจจับรุ่นย่อย (submodel) หรือ fallback เป็นคำหลังแบรนด์
  let model = null;
  if (brand) {
    const subs = carSubmodels[brand] || [];

    // ลอง match แบบตรงกับ submodel
    for (const sub of subs) {
      if (lower.includes(sub.toLowerCase())) {
        model = sub;
        break;
      }
    }

    // fallback: ดึงคำหลัง brand เช่น "honda civic 2022"
    if (!model) {
      const afterBrand = lower.split(brand.toLowerCase())[1]?.trim().split(" ")[0];
      if (afterBrand && afterBrand.length >= 3) {
        model = afterBrand.toUpperCase();
      }
    }
  }

  // ✅ ตรวจจับปี พ.ศ. / ค.ศ.
  const yearMatch = lower.match(/\b(20\d{2}|25\d{2})\b/);
  let year = null;
  if (yearMatch?.[0]) {
    const rawYear = parseInt(yearMatch[0], 10);
    year = rawYear > 2500 ? (rawYear - 543).toString() : rawYear.toString();
  }

  // ✅ ตรวจจับประเภทประกัน
  const typeMatch = lower.match(/(ชั้น\s*1|ชั้น\s*2\+|ชั้น\s*3\+|ชั้น\s*2|ชั้น\s*3|2\+|3\+|1|2|3)/i);
  const normalizeType = (typeRaw) => {
    if (!typeRaw) return null;
    const cleaned = typeRaw.replace(/ชั้น\s*/i, "").replace(/\s+/g, "").toLowerCase();
    if (["1", "2", "3", "2+", "3+"].includes(cleaned)) return cleaned;
    return null;
  };

  return {
    brand,
    model,
    year,
    insurance_type: normalizeType(typeMatch?.[0]),
  };
};
