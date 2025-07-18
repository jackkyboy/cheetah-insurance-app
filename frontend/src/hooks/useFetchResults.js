import { useState, useCallback } from "react";

/**
 * Custom hook for fetching data from an API with filters.
 *
 * @param {string} apiEndpoint - The API endpoint URL.
 * @returns {object} - { data, loading, error, fetchResults }
 */
const useFetchResults = (apiEndpoint) => {
  const [data, setData] = useState([]); // State to hold the fetched data
  const [loading, setLoading] = useState(false); // Loading state
  const [error, setError] = useState(null); // Error state

  /**
   * Fetch results from the API with given filters.
   *
   * @param {object} filters - The filters to apply to the API call.
   */
  const fetchResults = useCallback(
    async (filters) => {
      setLoading(true);
      setError(null);

      try {
        console.log("📤 Fetching results with filters:", filters);

        // Make the API call
        const response = await fetch(apiEndpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(filters),
        });

        const result = await response.json();

        if (response.ok) {
          console.log("📥 API response:", result);

          // Check if results are valid
          const results = Array.isArray(result.results)
            ? result.results
            : result.results
            ? Object.values(result.results).flat()
            : [];

          if (results.length === 0) {
            console.warn("⚠️ No results found");
          }

          setData(results);
        } else {
          console.error("❌ API Error:", result.message || "Unknown error");
          setError(result.message || "An error occurred while fetching data");
        }
      } catch (err) {
        console.error("❌ Fetch Error:", err.message || err);
        setError(err.message || "Failed to fetch results");
      } finally {
        setLoading(false);
      }
    },
    [apiEndpoint]
  );

  return { data, loading, error, fetchResults };
};

export default useFetchResults;
