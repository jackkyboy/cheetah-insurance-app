// /Users/apichet/Downloads/cheetah-insurance-app/src/components/MultiStepSearchResults.jsx
import React, { useState, useEffect, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import FiltersBar from "./FiltersBar";
import "../assets/styles/SearchResults.css";

const MultiStepSearchResults = ({
  initialResults = [],
  initialPage = 1,
  initialTotalPages = 1,
  companies = [],
  ratings = [],
  repairTypes = [],
}) => {
  const [filteredResults, setFilteredResults] = useState(initialResults);
  const [fallbacks, setFallbacks] = useState(null);
  const [appliedFilters, setAppliedFilters] = useState({});
  const [isFetchingResults, setIsFetchingResults] = useState(false);
  const [error, setError] = useState("");
  const [page, setPage] = useState(initialPage);
  const [totalPages, setTotalPages] = useState(initialTotalPages);

  const navigate = useNavigate();
  const location = useLocation();
  const formData = useRef(location.state?.filters || {});

  useEffect(() => {
    if (page > 0) fetchResults({ ...formData.current, page });
  }, [page]);

  useEffect(() => {
    if (location.state?.filters) {
      formData.current = location.state.filters;
      setPage(1);
      fetchResults({ ...formData.current, page: 1 });
    }
  }, [location.state]);


  
  const fetchResults = async (payload) => {
    setIsFetchingResults(true);
    setError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:5000/api/multi-step-search/fetch_packages",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }
      );

      const data = await response.json();
      console.log("✅ API Response:", data);

      if (response.ok) {
        const results = data.results || data.packages || data.available_filters?.results || [];
        console.log(`✅ Successfully fetched ${results.length} packages.`);

        setFilteredResults(results);
        if (data.fallbacks) {
          setFallbacks(data.fallbacks);
        }

        setPage(data.page || 1);
        setTotalPages(data.total_pages || 1);
      } else {
        setError(data.message || "เกิดข้อผิดพลาดในการดึงข้อมูล");
      }
    } catch (err) {
      console.error("❌ Error fetching results:", err);
      setError("เกิดข้อผิดพลาดระหว่างการดึงข้อมูล");
    } finally {
      setIsFetchingResults(false);
    }
  };
  const sanitizeLogoUrl = (company) => {
    const code = (company || "").toLowerCase().replace(/\s+/g, "").trim();
    return `/logos/${code}-logo.svg`;
  };
  
  const handleViewDetails = (packageData) => {
    if (!packageData?.package_code) {
      alert("ไม่มีข้อมูลแพ็กเกจสำหรับดูรายละเอียด");
      return;
    }
  
    const fallbackCompanyName = packageData.company_name || packageData.insurance_company || "ไม่ระบุบริษัท";
    const enrichedData = {
      ...packageData,
      company_full_name: packageData.company_full_name || fallbackCompanyName,
      insurance_company: packageData.insurance_company || fallbackCompanyName,
      logo_url: packageData.logo_url || sanitizeLogoUrl(fallbackCompanyName),
    };
  
    navigate(`/package-details/${enrichedData.package_code}`, {
      state: { packageData: enrichedData },
    });
  };
  
  
  const handleFiltersChange = (filters) => {
    setAppliedFilters(filters);
    setPage(1);
    fetchResults({ ...filters, page: 1 });
  };
  
  const handlePagination = (newPage) => {
    if (newPage > 0 && newPage <= totalPages) {
      setPage(newPage);
      fetchResults({ ...appliedFilters, page: newPage });
    }
  };
  

  const formatValue = (value, defaultText = "ไม่ระบุ") =>
    value ? value.toLocaleString() : defaultText;

  return (
    <div className="results-container">
      <h2>ผลลัพธ์การค้นหา (MultiStep)</h2>

      <div className="navigation-buttons">
        <button className="btn btn-secondary" onClick={() => navigate("/profile")}>กลับไปหน้าโปรไฟล์</button>
      </div>

      {fallbacks && (
        <div className="fallback-options">
          <h4>ไม่พบผลลัพธ์ ลองเลือกตัวเลือกอื่น:</h4>
          <p>ปีรถที่มีข้อมูล: {fallbacks.available_years.join(", ")}</p>
          <p>ประเภทประกันที่มีข้อมูล: {fallbacks.available_insurance_types.join(", ")}</p>
          <p>บริษัทที่ใกล้เคียง: {fallbacks.similar_companies.join(", ")}</p>

          {fallbacks.available_years.map((year) => (
            <button key={year} onClick={() => {
              formData.current = { ...formData.current, car_model_year: year };
              handleFiltersChange(formData.current);
            }}>
              ค้นหาปี {year}
            </button>
          ))}

          {fallbacks.available_insurance_types.map((type) => (
            <button key={type} onClick={() => {
              formData.current = { ...formData.current, insurance_type: type };
              handleFiltersChange(formData.current);
            }}>
              เลือกประเภท {type}
            </button>
          ))}

          {fallbacks.similar_companies.map((company) => (
            <button key={company} onClick={() => {
              formData.current = { ...formData.current, insurance_company: company };
              handleFiltersChange(formData.current);
            }}>
              เลือกบริษัท {company}
            </button>
          ))}
        </div>
      )}

      <FiltersBar onApplyFilters={handleFiltersChange} companies={companies} ratings={ratings} repairTypes={repairTypes} />

      {isFetchingResults ? (
        <div className="loading-container">
          <h2>กำลังโหลดข้อมูล...</h2>
          <div className="spinner"></div>
        </div>
      ) : error ? (
        <div className="error-container">
          <h2>เกิดข้อผิดพลาด</h2>
          <p>{error}</p>
        </div>
      ) : (
        <div className="card-grid">
          {filteredResults.length > 0 ? (
            filteredResults.map((result) => (
              <div key={result.package_code || result.id} className="card">
                <img
                  src={result.logo_url || "http://127.0.0.1:5000/logos/default-logo.svg"}
                  alt={`${result.company_name || "Default"} logo`}
                  className="company-logo"
                  onError={(e) => (e.target.src = "http://127.0.0.1:5000/logos/default-logo.svg")}
                />
                <h3>{result.company_name || "ไม่ระบุบริษัท"}</h3>
                <p><strong>รหัสแพ็กเกจ:</strong> {result.package_code || "ไม่ระบุ"}</p>
                <p><strong>เบี้ยประกัน:</strong> {formatValue(result.premium)} บาท</p>
                <p><strong>ประเภทการซ่อม:</strong> {result.repair_type || "ไม่ระบุ"}</p>
                <p><strong>ประภทประกันภัย:</strong> {result.insurance_type || "ไม่ระบุ"}</p>
                <p><strong>รุ่นย่อย:</strong> {result.car_submodel || "ไม่ระบุ"}</p>
                <button
                  className="view-details-btn"
                  onClick={() => handleViewDetails(result)}
                  disabled={!result.package_code}
                >
                  ดูรายลเอียด
                </button>
              </div>
            ))
          ) : (
            <p className="no-results">ไม่มีผลลัพธ์การค้นหา</p>
          )}
        </div>
      )}

      {totalPages > 1 && (
        <div className="pagination">
          <button
            className="pagination-btn"
            onClick={() => handlePagination(page - 1)}
            disabled={page <= 1}
          >
            ก่อนหน้า
          </button>
          <span>
            หน้า {page} จาก {totalPages}
          </span>
          <button
            className="pagination-btn"
            onClick={() => handlePagination(page + 1)}
            disabled={page >= totalPages}
          >
            ถัดไป
          </button>
        </div>
      )}
    </div>
  );
};

export default MultiStepSearchResults;
