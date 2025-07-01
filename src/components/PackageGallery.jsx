// /Users/apichet/Downloads/cheetah-insurance-app/src/components/package_gallery.jsx
// ✅ /Users/apichet/Downloads/cheetah-insurance-app/src/components/PackageGallery.jsx
import React, { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { fetchGalleryPackages, fetchCarModels, fetchModelYears } from "../api/gallery";
import { FixedSizeList as List } from "react-window";
import InfiniteLoader from "react-window-infinite-loader";
import "../assets/styles/gallery.css";
import DeconstructedCarousel from "./DeconstructedCarousel";


// ✅ ALL_BRANDS เต็มรูปแบบ
export const ALL_BRANDS = [
  "AC", "AIRSTREAM", "ALFA", "ALFA ROMEO", "ASTON MARTIN", "AUDI",
  "BENTLEY", "BMW", "BRABUS", "BYD", "CADILLAC", "CHERY", "CHEVROLET",
  "CHRYSLER", "CITROEN", "DAEWOO", "DAIHATSU", "DFM", "DFSK", "DONGFENG",
  "FERRARI", "FIAT", "FOMM", "FORD", "FOTON", "GWM TANK", "HAVAL",
  "HOLDEN", "HONDA", "HUMMER", "HYUNDAI", "ISUZU", "JAGUAR", "JEEP",
  "JONWAY", "KIA", "LAMBORGHINI", "LAND ROVER", "LEXUS", "LOTUS",
  "MASERATI", "MAXUS", "MAZDA", "MCLAREN", "MERCEDES-BENZ", "MG", "MINI",
  "MITSUBISHI", "MITSUOKA", "NAZA", "NETA", "NISSAN", "OPEL", "ORA",
  "PEUGEOT", "PORSCHE", "PROTON", "RANGE ROVER", "RENAULT", "ROLLSROYCE",
  "ROVER", "SAAB", "SEAT", "SKODA", "SOKON", "SSANGYONG", "SUBARU",
  "SUZUKI", "TATA", "TESLA", "THAI RUNG", "THAIRUNG", "TOYOTA", "TR",
  "VOLKSWAGEN", "VOLT", "VOLVO"
];

const TOP_BRANDS = [
  "TOYOTA", "ISUZU", "HONDA", "NISSAN", "FORD",
  "MAZDA", "MITSUBISHI", "CHEVROLET", "MERCEDES-BENZ", "TR"
];

const COMPANY_INFO = {
  "chubb": {
    name: "ชับบ์",
    logo: "/gallery_logos/partners/CHUBB-logo.svg",
  },
  "ergo": {
    name: "ERGO",
    logo: "/gallery_logos/partners/ERGO-logo.svg",
  },
  "mti": {
    name: "เมืองไทยประกันภัย",
    logo: "/gallery_logos/partners/MTI-logo.svg",
  },
  "viriyah": {
    name: "วิริยะ",
    logo: "/gallery_logos/partners/VIRIYAH-logo.svg",
  },
  "axa": {
    name: "AXA",
    logo: "/gallery_logos/partners/AXA-logo.svg",
  },
  "dhip": {
    name: "ทิพยประกันภัย",
    logo: "/gallery_logos/partners/DHIP-logo.svg",
  },
  "kpi": {
    name: "กรุงไทยพานิช",
    logo: "/gallery_logos/partners/KPI-logo.svg",
  },
  "msig": {
    name: "MSIG",
    logo: "/gallery_logos/partners/MSIG-logo.svg",
  },
  "tki": {
    name: "โตเกียวมารีน",
    logo: "/gallery_logos/partners/TKI-logo.svg",
  },
  "fal": {
    name: "ฟอลคอน",
    logo: "/gallery_logos/partners/FAL-logo.svg",
  },
};


const limit = 30;
const PackageGallery = () => {
  const [expandedIndex, setExpandedIndex] = useState(null);
  const [viewMode, setViewMode] = useState("infinite"); // 🔁 หรือ "carousel"
  const [packages, setPackages] = useState([]);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  const [selectedBrand, setSelectedBrand] = useState(null);
  const [selectedType, setSelectedType] = useState(null);
  const [selectedModel, setSelectedModel] = useState(null);
  const [selectedYear, setSelectedYear] = useState(null);
  const [selectedCompany, setSelectedCompany] = useState(null);
  

  const [models, setModels] = useState([]);
  const [years, setYears] = useState([]);

  const limit = 30; // ✅ อยู่ภายในฟังก์ชัน ไม่ซ้ำซ้อนกับตัวบนสุด

  const enrichCompanyInfo = (pkg) => {
    const raw = (pkg.insurance_company || "").trim().toLowerCase();
    const matched = Object.keys(COMPANY_INFO).find((key) =>
      raw.includes(key.toLowerCase())
    );

    if (matched) {
      return {
        ...pkg,
        company_full_name: COMPANY_INFO[matched].name,
        company_logo: COMPANY_INFO[matched].logo,
      };
    }

    return {
      ...pkg,
      company_full_name: pkg.insurance_company || "ไม่ระบุบริษัท",
      company_logo: "/gallery_logos/partners/default-logo.svg",
    };
  };

  const getCompanyCodeByName = (name) => {
    const entry = Object.entries(COMPANY_INFO).find(([, val]) => val.name === name);
    return entry ? entry[0] : null;
  };

  const fetchData = async (currentPage = 0, reset = false) => {
    if (isLoading) return;
    setIsLoading(true);

    try {
      const offset = currentPage * limit;

      const res = await fetchGalleryPackages({
        brand: selectedBrand,
        model: selectedModel,
        year: selectedYear,
        type: selectedType,
        company: selectedCompany || null,
        limit,
        offset,
      });

      const enriched = Array.isArray(res) ? res.map(enrichCompanyInfo) : [];

      if (reset) {
        setPackages(enriched);
        setPage(1);
      } else {
        setPackages((prev) => [...prev, ...enriched]);
        setPage((prev) => prev + 1);
      }

      setHasMore(enriched.length === limit);
    } catch (err) {
      console.error("❌ fetch error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadMoreItems = () => {
    if (!hasMore || isLoading) return;
    fetchData(page);
  };

  const isItemLoaded = (index) => !hasMore || index < packages.length;

  useEffect(() => {
    setPackages([]);
    setPage(0);
    setHasMore(true);
    fetchData(0, true);
  }, [selectedBrand, selectedType, selectedModel, selectedYear, selectedCompany]);

  useEffect(() => {
    if (!selectedBrand) {
      setModels([]);
      setSelectedModel(null);
      return;
    }
    fetchCarModels(selectedBrand).then(setModels).catch(console.error);
  }, [selectedBrand]);

  useEffect(() => {
    if (!selectedModel || !selectedBrand) {
      setYears([]);
      setSelectedYear(null);
      return;
    }
    fetchModelYears(selectedBrand, selectedModel).then(setYears).catch(console.error);
  }, [selectedModel, selectedBrand]);

  const getCompanyDisplay = (pkg) => {
    return {
      name:
        pkg.company_full_name ||
        COMPANY_INFO[pkg.insurance_company_code]?.name ||
        pkg.insurance_company ||
        "ไม่ระบุบริษัท",
      logo:
        pkg.company_logo ||
        COMPANY_INFO[pkg.insurance_company_code]?.logo ||
        "/gallery_logos/partners/default-logo.svg",
    };
  };

  const Row = ({ index, style }) => {
    const pkg = packages[index];
    const navigate = useNavigate();
  
    if (!pkg) return null;
  
    const enrichedPkg = enrichCompanyInfo(pkg);
    const { name: companyName, logo: logoSrc } = getCompanyDisplay(enrichedPkg);
  
    return (
      <div style={{ ...style, padding: "10px" }}>
        <div className="gallery-card cheetah-gradient d-flex flex-column justify-between h-100">
          
          {/* ✅ ส่วนบน (ข้อมูลบริษัท + รายละเอียดแพ็คเกจ) */}
          <div className="flex-grow-1">
            <div className="d-flex align-items-center mb-2">
              <img
                src={logoSrc}
                alt={companyName}
                style={{
                  width: "32px",
                  height: "32px",
                  objectFit: "contain",
                  marginRight: "12px",
                  background: "#fff",
                  borderRadius: "50%",
                  padding: "4px"
                }}
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = "/gallery_logos/partners/default-logo.svg";
                }}
              />
              <h5 className="gallery-card-title m-0">{companyName}</h5>
            </div>
  
            <div className="mb-2 small">
              ประเภท: <strong>{enrichedPkg.insurance_type || "-"}</strong> • {enrichedPkg.repair_type || "-"}
            </div>
  
            <ul className="list-unstyled small mb-2">
              <li>🚗 <strong>ยี่ห้อ:</strong> {enrichedPkg.car_brand || "-"}</li>
              <li>📆 <strong>ปีรถ:</strong> {enrichedPkg.car_model_year || "-"}</li>
              <li>🔢 <strong>รุ่น:</strong> {enrichedPkg.car_model || "-"} / {enrichedPkg.car_submodel || "-"}</li>
              <li>
                💰 <strong>เบี้ยรวม:</strong>{" "}
                <span className="fw-bold">
                  {enrichedPkg.premium ? parseFloat(enrichedPkg.premium).toLocaleString() : "N/A"} บาท
                </span>
              </li>
            </ul>
          </div>
  
          {/* 🔽 ปุ่มแสดงรายละเอียด - อยู่ล่างสุดเสมอ */}
          <div className="text-center mt-auto">
            <button
              className="gallery-btn-details"
              onClick={() =>
                navigate(`/package/${enrichedPkg.package_code}`, {
                  state: { packageData: enrichedPkg },
                })
              }
            >
              📄 รายละเอียด
            </button>
          </div>
  
        </div>
      </div>
    );
  };
  
  
  
  
  
  return (
    <div className="gallery-container">
      <h2 className="gallery-heading">🛡️ แพ็กเกจประกันภัยแนะนำ</h2>
  
      {/* 🔽 Filters */}
      <div className="gallery-filters mb-4 row g-3">
        {/* ยี่ห้อรถ */}
        <div className="col-md-3">
          <label className="form-label">ยี่ห้อ</label>
          <select
            className="form-select"
            value={selectedBrand || ""}
            onChange={(e) => setSelectedBrand(e.target.value || null)}
          >
            <option value="">ทั้งหมด</option>
            {ALL_BRANDS.map((brand) => (
              <option key={brand} value={brand}>
                {brand}
              </option>
            ))}
          </select>
        </div>
  
        {/* รุ่นรถ */}
        <div className="col-md-3">
          <label className="form-label">รุ่น</label>
          <select
            className="form-select"
            value={selectedModel || ""}
            onChange={(e) => setSelectedModel(e.target.value || null)}
            disabled={!models.length}
          >
            <option value="">ทั้งหมด</option>
            {models.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
        </div>
  
        {/* ปี */}
        <div className="col-md-2">
          <label className="form-label">ปี</label>
          <select
            className="form-select"
            value={selectedYear || ""}
            onChange={(e) => setSelectedYear(e.target.value || null)}
            disabled={!years.length}
          >
            <option value="">ทั้งหมด</option>
            {years.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </div>
  
        {/* ประเภทประกัน */}
        <div className="col-md-2">
          <label className="form-label">ประเภทประกัน</label>
          <select
            className="form-select"
            value={selectedType || ""}
            onChange={(e) => setSelectedType(e.target.value || null)}
          >
            <option value="">ทั้งหมด</option>
            <option value="1">ชั้น 1</option>
            <option value="2+">2+</option>
            <option value="2">2</option>
            <option value="3+">3+</option>
            <option value="3">3</option>
          </select>
        </div>
  
        {/* บริษัทประกัน */}
        <div className="col-md-2">
          <label className="form-label">บริษัทประกัน</label>
          <select
            className="form-select"
            value={selectedCompany || ""}
            onChange={(e) => setSelectedCompany(e.target.value || null)}
          >
            <option value="">ทั้งหมด</option>
            {Object.entries(COMPANY_INFO).map(([code, info]) => (
              <option key={code} value={code}>
                {info.name}
              </option>
            ))}
          </select>
        </div>
      </div>
  
      {/* 🔁 ปุ่มสลับมุมมอง */}
      <div className="view-toggle-buttons mb-4">
        <span className="fw-bold mb-2 me-2">แสดงผลแบบ:</span>
        <div className="d-flex gap-2 flex-wrap">
          <button
            type="button"
            className={`filter-btn ${viewMode === "infinite" ? "active" : ""}`}
            onClick={() => setViewMode("infinite")}
          >
            🔁 เลื่อนต่อเนื่อง
          </button>
          <button
            type="button"
            className={`filter-btn ${viewMode === "carousel" ? "active" : ""}`}
            onClick={() => setViewMode("carousel")}
          >
            🎠 แสดงแบบ 3D
          </button>
        </div>
      </div>


      {/* 🔽 การแสดงผลแพ็กเกจ */}
      {viewMode === "infinite" ? (
        <InfiniteLoader
          isItemLoaded={isItemLoaded}
          itemCount={hasMore ? packages.length + 1 : packages.length}
          loadMoreItems={loadMoreItems}
        >
          {({ onItemsRendered, ref }) => (
            <List
              height={window.innerWidth < 768 ? 500 : 600}        // ⬅ ปรับความสูง
              itemSize={window.innerWidth < 768 ? 220 : 250}      // ⬅ ปรับขนาดต่อรายการ
              itemCount={packages.length}
              width={"100%"}
              onItemsRendered={onItemsRendered}
              ref={ref}
            >
              {Row}
            </List>
          )}
        </InfiniteLoader>
      ) : (
        <DeconstructedCarousel packages={packages} />
      )}

    </div>
  );
  
  

  
};

export default PackageGallery;

