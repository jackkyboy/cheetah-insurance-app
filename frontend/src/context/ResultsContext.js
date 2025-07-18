// /Users/apichet/Downloads/cheetah-insurance-app/src/context/ResultsContext.js
import React, { createContext, useState, useContext, useCallback } from "react";

// Create the ResultsContext
const ResultsContext = createContext();

// Provider component to wrap the application
export const ResultsProvider = ({ children }) => {
  const [filters, setFilters] = useState({});
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    totalPages: 1,
    itemsPerPage: 10,
  });
  const [sortBy, setSortBy] = useState(null);

  // Function to fetch results using filters
  const fetchResults = useCallback(async (apiEndpoint, newFilters = {}, page = 1) => {
    setLoading(true);
    setError(null);
  
    try {
      console.log("📤 Request Payload:", {
        ...newFilters,
        page,
        limit: pagination.itemsPerPage,
      });
  
      const response = await fetch(apiEndpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...newFilters,
          page,
          limit: pagination.itemsPerPage,
        }),
      });
  
      const data = await response.json();
  
      console.log("✅ API Response:", data);
  
      if (response.ok && data.results) {
        const formattedResults = Array.isArray(data.results)
          ? data.results
          : Object.values(data.results).flat();
  
        setFilters(newFilters);
        setResults(formattedResults);
        setPagination((prev) => ({
          ...prev,
          page: data.page || page,
          totalPages: data.total_pages || 1,
        }));
      } else {
        console.error("❌ API Error:", data.message || "Unknown error");
        setError(data.message || "Failed to fetch results");
      }
    } catch (err) {
      console.error("❌ Fetch Error:", err.message || err);
      setError(err.message || "Failed to fetch results");
    } finally {
      setLoading(false);
    }
  }, [pagination.itemsPerPage]);
  

  // Function to update the page
  const updatePage = (newPage) => {
    console.log("🔄 Updating Page:", newPage);
    if (newPage > 0 && newPage <= pagination.totalPages) {
      setPagination((prev) => ({ ...prev, page: newPage }));
    } else {
      console.warn(`⚠️ Invalid page number: ${newPage}`);
    }
  };
  

  // Function to handle sorting
  const applySorting = (sortKey) => {
    setSortBy(sortKey);

    if (results.length > 0) {
      const sortedResults = [...results].sort((a, b) => {
        if (a[sortKey] < b[sortKey]) return -1;
        if (a[sortKey] > b[sortKey]) return 1;
        return 0;
      });

      setResults(sortedResults);
    }
  };

  return (
    <ResultsContext.Provider
      value={{
        filters,
        results,
        loading,
        error,
        pagination,
        sortBy,
        setFilters,
        fetchResults,
        updatePage,
        applySorting,
      }}
    >
      {children}
    </ResultsContext.Provider>
  );
};

// Custom hook to use the ResultsContext
export const useResults = () => {
  const context = useContext(ResultsContext);
  if (!context) {
    throw new Error("useResults must be used within a ResultsProvider");
  }
  return context;
};
