import { useState, useEffect } from "react";

const useCarData = ({
  fetchCarModels,
  fetchSubModels,
  fetchCarModelYears,
}) => {
  const [carModels, setCarModels] = useState([]);
  const [subModels, setSubModels] = useState([]);
  const [carModelYears, setCarModelYears] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchModels = async (carBrand) => {
    setLoading(true);
    try {
      const models = await fetchCarModels(carBrand);
      setCarModels(models || []);
    } catch (err) {
      setError("ไม่สามารถดึงข้อมูลรุ่นรถยนต์ได้");
    } finally {
      setLoading(false);
    }
  };

  const fetchSubModelsData = async (carBrand, carModel) => {
    setLoading(true);
    try {
      const models = await fetchSubModels(carBrand, carModel);
      setSubModels(models || []);
    } catch (err) {
      setError("ไม่สามารถดึงข้อมูลรุ่นย่อยได้");
    } finally {
      setLoading(false);
    }
  };

  const fetchYears = async (carBrand, carModel, carSubModel) => {
    setLoading(true);
    try {
      const years = await fetchCarModelYears(carBrand, carModel, carSubModel);
      setCarModelYears(years.sort((a, b) => b - a) || []);
    } catch (err) {
      setError("ไม่สามารถดึงข้อมูลปีรถยนต์ได้");
    } finally {
      setLoading(false);
    }
  };

  return {
    carModels,
    subModels,
    carModelYears,
    loading,
    error,
    fetchModels,
    fetchSubModelsData,
    fetchYears,
  };
};

export default useCarData;
