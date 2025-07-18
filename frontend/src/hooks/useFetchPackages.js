///Users/apichet/Downloads/cheetah-insurance-app/src/hooks/useFetchPackages.js
import { useState, useCallback, useRef } from "react";
import { fetchInsurancePackages, fetchPackagesWithLogos } from "../api/api";

const useFetchPackages = (initialFilters = {}) => {
  const [packages, setPackages] = useState([]);
  const [logos, setLogos] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({ page: 1, totalPages: 1 });

  const logosFetched = useRef(false);

  const fetchLogos = useCallback(async () => {
    if (logosFetched.current) return;

    try {
      const packagesWithLogos = await fetchPackagesWithLogos();
      const logoMapping = packagesWithLogos.reduce((map, item) => {
        map[item.insurance_company] = item.logo_url;
        return map;
      }, {});
      setLogos(logoMapping);
      logosFetched.current = true;
    } catch (err) {
      console.error("Error fetching logos:", err.message);
    }
  }, []);

  const fetchData = useCallback(
    async (filters, page = 1, limit = 5) => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetchInsurancePackages({ ...filters, page, limit });
        if (response && response.results) {
          setPackages(response.results);
          setPagination({ page: response.page || 1, totalPages: response.total_pages || 1 });
        } else {
          throw new Error("Invalid API response structure.");
        }
      } catch (err) {
        setError(err.message || "Failed to fetch data.");
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    packages,
    logos,
    loading,
    error,
    pagination,
    fetchData,
    fetchLogos,
  };
};

export default useFetchPackages;
