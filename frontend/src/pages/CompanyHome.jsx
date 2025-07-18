// /Users/apichet/Downloads/cheetah-insurance-app/src/pages/CompanyHome.jsx
import React, { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";

import Header from "../components/Header";
import Footer from "../components/Footer";
import MultiStepSearch from "../components/MultiStepSearch";
import StepForm from "../components/StepForm";

import {
  fetchCarBrands,
  fetchCarModels,
  fetchCarSubModels,
  fetchCarModelYears,
  fetchInsuranceTypes,
} from "../api/multiStepSearchService";

import { useAuth } from "../context/AuthContext";
import "../assets/styles/CompanyHome.css";

const CompanyHome = () => {
  const navigate = useNavigate();
  const { authToken } = useAuth();

  const [carBrands, setCarBrands] = useState([]);
  const [insuranceTypes, setInsuranceTypes] = useState([]);
  const [activeForm, setActiveForm] = useState("voluntary");
  const hasFetched = useRef(false);

  // --- Utils ---
  const isUserAuthenticated = () => !!authToken;
  const sortByThaiLocale = (arr) =>
    Array.isArray(arr) ? arr.sort((a, b) => a.localeCompare(b, "th")) : [];

  // --- Initial Data Fetch ---
  useEffect(() => {
    if (hasFetched.current) return;

    const fetchData = async () => {
      try {
        const [brands, types] = await Promise.all([
          fetchCarBrands(),
          fetchInsuranceTypes(),
        ]);

        setCarBrands(sortByThaiLocale(brands));
        setInsuranceTypes(sortByThaiLocale(types));
      } catch (err) {
        console.error("❌ Error fetching data:", err);
      } finally {
        hasFetched.current = true;
      }
    };

    fetchData();
  }, []);

  // --- Navigation Handlers ---
  const handleSearch = (payload) => {
    if (!payload) return console.warn("❌ Invalid search payload");
    navigate("/search-results", { state: { searchPayload: payload } });
  };

  const goTo = (path) => navigate(path);

  // --- Render ---
  return (
    <div className="company-home">
      <Header />

      <main className="company-body">
        {/* 🔶 Hero Section */}
        <section className="hero-section">
          <h1 className="hero-title gradient-text">Cheetah Insurance Broker</h1>
          <p className="hero-subtitle">
            เปรียบเทียบราคาประกันรถยนต์อย่างรวดเร็ว ง่าย และไว้วางใจได้
          </p>

          <div className="hero-buttons">
            {!isUserAuthenticated() && (
              <button className="btn-primary" onClick={() => goTo("/login")}>
                🔑 เข้าสู่ระบบ
              </button>
            )}
            <button className="btn-secondary" onClick={() => goTo("/chat-agent")}>
              💬 คุยกับแชทเอเจนต์
            </button>
            <button className="btn-secondary" onClick={() => goTo("/gallery")}>
              🖼️ แพ็กเกจทั้งหมด
            </button>
          </div>
        </section>

        {/* 🧭 Switcher */}
        <section className="insurance-switcher">
          <button
            className={`switch-btn ${activeForm === "voluntary" ? "active" : ""}`}
            onClick={() => setActiveForm("voluntary")}
          >
            เลือกซื้อประกันภัยสมัครใจ
          </button>
          <button
            className={`switch-btn ${activeForm === "compulsory" ? "active" : ""}`}
            onClick={() => setActiveForm("compulsory")}
          >
            ประกันภัยภาคบังคับ (พรบ.)
          </button>
        </section>

        {/* 📋 Search Form */}
        <section className="search-section">
          {activeForm === "voluntary" ? (
            <MultiStepSearch
              onSearch={handleSearch}
              carBrands={carBrands}
              fetchCarModels={fetchCarModels}
              fetchSubModels={fetchCarSubModels}
              fetchCarModelYears={fetchCarModelYears}
              insuranceTypes={insuranceTypes}
            />
          ) : (
            <StepForm
              onSearch={handleSearch}
              carBrands={carBrands}
              insuranceTypes={insuranceTypes}
            />
          )}
        </section>
      </main>

      <Footer />
    </div>
  );
};

export default CompanyHome;
