// /Users/apichet/Downloads/cheetah-insurance-app/src/components/PackageList.jsx
import React, { useEffect, useState, useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { fetchInsurancePackages } from "../api/api";
import FiltersBar from "./FiltersBar";
import PackageCard from "./PackageCard";
import "../assets/styles/PackageList.css";

const DEFAULT_FILTERS = {
  car_brand: "Toyota",
  car_model: "Camry",
  car_model_year: "2022",
  car_submodel: "",
  insurance_type: "1",
  repair_type: "repair_shop",
  premium_min: 0,
  premium_max: 99999999,
  page: 1,
  limit: 10,
};

const insuranceTypeMapping = {
  "1": "1", "2": "2", "2+": "2+", "2p": "2+", "3": "3", "3+": "3+", "3p": "3+",
  car: "1", "": "0", "0": "0"
};

const PackageList = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({ page: 1, totalPages: 1 });
  const [appliedFilters, setAppliedFilters] = useState(DEFAULT_FILTERS);

  const validateFilters = (filters) => {
    const rawType = filters.insuranceType || filters.insurance_type || "";
    const normalizedType = insuranceTypeMapping[rawType.trim().toLowerCase()] || rawType.trim();
    return {
      ...DEFAULT_FILTERS,
      ...filters,
      insurance_type: normalizedType,
      page: filters.page || 1,
      limit: filters.limit || 10,
      year: filters.car_model_year || filters.year,
    };
  };

  const fetchData = async (filters) => {
    setLoading(true);
    setError(null);
    try {
      const validated = validateFilters(filters);
      const res = await fetchInsurancePackages(validated);
      const results = Object.values(res?.results || {}).flat();
      setPackages(results);
      setPagination({ page: res.page || 1, totalPages: res.total_pages || 1 });
    } catch (err) {
      setError(err.message || "ไม่สามารถโหลดแพ็กเกจได้");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (location.state?.filters) {
      const normalized = validateFilters(location.state.filters);
      const isSame = JSON.stringify(normalized) === JSON.stringify(validateFilters(appliedFilters));
      if (!isSame) {
        setAppliedFilters(normalized);
        fetchData(normalized);
      }
    } else {
      fetchData(appliedFilters);
    }
  }, [location.state]);

  const handleFiltersChange = (newFilters) => {
    const merged = { ...appliedFilters, ...newFilters, page: 1 };
    setAppliedFilters(merged);
    fetchData(merged);
  };

  const handleNavigateToPackage = (pkg) => {
    const id = pkg.package_code || pkg.id || pkg.policy_code;
    if (!id) return alert("ไม่พบรหัสแพ็กเกจ");
    navigate(`/package/${encodeURIComponent(id)}`, { state: { packageData: pkg } });
  };

  const renderedPackages = useMemo(() => {
    if (!Array.isArray(packages) || packages.length === 0) {
      return <p>🚫 ไม่มีแพ็คเกจที่จะแสดง</p>;
    }

    return packages.map((pkg, i) => (
      <li key={i} className="package-card">
        <PackageCard
          pkg={{ ...pkg, is_featured: true }}
          onViewFullDetails={handleNavigateToPackage}
        />
      </li>
    ));
  }, [packages]);

  if (loading) return <p className="loading-message">⏳ กำลังโหลดข้อมูล...</p>;
  if (error) return <div className="error-container"><p className="error-message">❌ {error}</p></div>;

  return (
    <div className="package-list">
      <FiltersBar
        onApplyFilters={handleFiltersChange}
        companies={[...new Set(packages.map((p) => p.company_name))]}
        initialFilters={appliedFilters}
      />
      <div className="package-header"><h2>รายการแพ็คเกจประกันภัย</h2></div>
      <ul className="package-grid">{renderedPackages}</ul>
    </div>
  );
};

export default PackageList;
