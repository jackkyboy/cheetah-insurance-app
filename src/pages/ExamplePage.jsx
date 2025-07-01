// src/pages/ExamplePage.jsx
import React, { useEffect } from "react";
import { useLoader } from "../contexts/GlobalLoaderContext";
import { fetchInsurancePackages } from "../api/api";

const ExamplePage = () => {
  const { setIsLoading } = useLoader();

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true); // เริ่มแสดง Loader
      try {
        const data = await fetchInsurancePackages();
        console.log("✅ Data fetched:", data);
      } catch (error) {
        console.error("❌ Error fetching data:", error);
      } finally {
        setIsLoading(false); // ซ่อน Loader เมื่อโหลดเสร็จ
      }
    };

    fetchData();
  }, [setIsLoading]);

  return <div>Example Page Content</div>;
};

export default ExamplePage;
