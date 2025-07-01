// /Users/apichet/Downloads/cheetah-insurance-app/src/components/SearchResults.jsx
import React, { useState, useEffect, useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import PackagePopup from "./PackagePopup";
import { getInsuranceDetails } from "../api/mandatoryInsuranceMapping";
import "../assets/styles/SearchResults.css";
import FallbackSuggestions from "./FallbackSuggestions";
import { fetchFallbackSuggestions } from "../api/carService";

const SearchResults = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const { results: initialResults = [], searchParams = {} } = location.state || {};
  const [logos, setLogos] = useState({});
  const [selectedPackage, setSelectedPackage] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [sortOption, setSortOption] = useState("default");
  const [fallbacks, setFallbacks] = useState(null);
  const itemsPerPage = 10;
  const [showFallbackNotice, setShowFallbackNotice] = useState(false);

  useEffect(() => {
    const tryFetchFallbacks = async () => {
      if (initialResults.length === 0) {
        const { car_brand, car_model } = searchParams;
        if (car_brand && car_model) {
          try {
            const fallbackData = await fetchFallbackSuggestions(car_brand, car_model);
            setFallbacks(fallbackData);
          } catch (error) {
            console.error("❌ Fallback fetch error:", error.message);
          }
        }
      }
    };
    tryFetchFallbacks();
  }, [initialResults, searchParams]);

  useEffect(() => {
    if (fallbacks && !initialResults.length) {
      setShowFallbackNotice(true);
    }
  }, [fallbacks, initialResults]);

  const filteredResults = useMemo(() => {
    return initialResults.filter(row =>
      row.insurance_type === "0" && row.premium && !isNaN(parseFloat(row.premium))
    );
  }, [initialResults]);

  const sortedResults = useMemo(() => {
    if (sortOption === "premium_asc") {
      return [...filteredResults].sort((a, b) => parseFloat(a.premium) - parseFloat(b.premium));
    }
    if (sortOption === "premium_desc") {
      return [...filteredResults].sort((a, b) => parseFloat(b.premium) - parseFloat(a.premium));
    }
    return filteredResults;
  }, [filteredResults, sortOption]);

  const paginatedResults = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage;
    return sortedResults.slice(start, start + itemsPerPage);
  }, [sortedResults, currentPage]);

  const totalPages = Math.ceil(filteredResults.length / itemsPerPage);

  const sanitizeLogoUrl = (url) => {
    const baseUrl = process.env.REACT_APP_BACKEND_URL || "http://127.0.0.1:5000";
    return !url || url.includes("default-logo.svg")
      ? `${baseUrl}/logos/default-logo.svg`
      : url.startsWith("http") ? url : `${baseUrl}${url}`;
  };

  useEffect(() => {
    const fetchLogos = async () => {
      try {
        const res = await fetch("http://127.0.0.1:5000/api/car-options/packages_with_logos");
        const data = await res.json();
        const logoMap = data.results.reduce((acc, item) => {
          acc[item.insurance_company] = sanitizeLogoUrl(item.logo_url);
          return acc;
        }, {});
        setLogos(logoMap);
      } catch (err) {
        console.error("❌ Fetch logos failed:", err.message);
      }
    };
    fetchLogos();
  }, []);

  const handleBuyPackage = (pkg) => {
    const paymentUrl = `https://sandbox-2c2p.example.com/pay?packageCode=${pkg.package_code}`;
    window.location.href = paymentUrl;
  };

  const renderedPackages = useMemo(() => {
    if (!filteredResults.length) {
      return (
        <div className="no-results">
          <p>🚫 ไม่มีแพ็คเกจที่ตรงกับเงื่อนไข</p>
          {fallbacks ? (
            <FallbackSuggestions
              availableYears={fallbacks.available_years}
              insuranceTypes={fallbacks.available_insurance_types}
              insuranceCompanies={fallbacks.similar_companies}
              onSelect={(type, value) => {
                console.log("🔁 User selected fallback:", type, value);
              }}
            />
          ) : (
            <p>⏳ กำลังค้นหาทางเลือกเพิ่มเติม...</p>
          )}
        </div>
      );
    }

    return paginatedResults.map((pkg, index) => {
      const logoUrl = logos[pkg.company_name] || sanitizeLogoUrl(null);
      const insuranceDetails = getInsuranceDetails(
        pkg.car_model,
        "personal",
        parseInt(pkg.car_model_year)
      );

      return (
        <div key={index} className="card">
          <img
            src={logoUrl}
            alt={`${pkg.company_name || "โลโก้เริ่มต้น"} logo`}
            className="company-logo"
            onError={(e) => (e.target.src = sanitizeLogoUrl(null))}
          />
          <h3>{pkg.company_name || "ไม่ระบุบริษัท"}</h3>

          <p><strong>เบี้ย พรบ.:</strong> {insuranceDetails?.total || "ไม่ระบุ"} บาท</p>
          <p><strong>ปีของรถ:</strong> {pkg.car_model_year || "ไม่ระบุ"}</p>
          <p><strong>รุ่นรถ:</strong> {pkg.car_model || "ไม่ระบุ"}</p>
          <p><strong>ยี่ห้อรถ:</strong> {pkg.car_brand || "ไม่ระบุ"}</p>

          {insuranceDetails && !insuranceDetails.error && (
            <p><strong>รหัส พรบ.:</strong> {insuranceDetails.code}</p>
          )}

          <div className="card-actions">
            <button onClick={() => setSelectedPackage(pkg)} className="popup-btn">
              ตารางความคุ้มครอง
            </button>
            <button onClick={() => handleBuyPackage(pkg)} className="buy-btn">
              ซื้อ
            </button>
          </div>
        </div>
      );
    });
  }, [filteredResults, paginatedResults, logos, fallbacks]);

  return (
    <div className="results-container">
      <h2>ผลลัพธ์การค้นหา</h2>

      <div className="navigation-links">
        <button onClick={() => navigate("/profile")} className="navigation-btn">
          กลับไปหน้าโปรไฟล์
        </button>
        <button onClick={() => navigate("/")} className="navigation-btn">
          กลับไปหน้าแรก
        </button>
      </div>

      <div className="sort-options">
        <label htmlFor="sort-select">จัดเรียง:</label>
        <select
          id="sort-select"
          value={sortOption}
          onChange={(e) => setSortOption(e.target.value)}
        >
          <option value="default">ค่าเริ่มต้น</option>
          <option value="premium_asc">เบี้ยประกัน (น้อยไปมาก)</option>
          <option value="premium_desc">เบี้ยประกัน (มากไปน้อย)</option>
        </select>
      </div>

      {showFallbackNotice && (
        <div className="fallback-warning">
          <p>
            🚨 <strong>ไม่พบแพ็กเกจสำหรับรถ {searchParams.car_brand} {searchParams.car_model} ปี {searchParams.car_model_year}</strong>
          </p>
          <p>
            แสดงแพ็กเกจที่ใกล้เคียงจากยี่ห้อและรุ่นอื่นแทน เช่น Toyota Camry ปี 2022
          </p>
          <button className="fallback-retry-btn" onClick={() => navigate("/search")}>🔄 ลองค้นหาใหม่</button>
        </div>
      )}

      <div className="card-grid">{renderedPackages}</div>

      {totalPages > 1 && (
        <div className="pagination">
          <button
            onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
            disabled={currentPage <= 1}
            className="pagination-btn"
          >
            ก่อนหน้า
          </button>
          <span>หน้า {currentPage} จาก {totalPages}</span>
          <button
            onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
            disabled={currentPage >= totalPages}
            className="pagination-btn"
          >
            ถัดไป
          </button>
        </div>
      )}

      {selectedPackage && (
        <PackagePopup
          packageData={selectedPackage}
          onClose={() => setSelectedPackage(null)}
        />
      )}
    </div>
  );
};

export default SearchResults;
