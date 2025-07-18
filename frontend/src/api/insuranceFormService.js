import axios from "axios";

const BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:5000/api";

export const saveInsuranceForm = async (formData) => {
  try {
    const response = await axios.post(`${BASE_URL}/insurance/prepare`, formData);
    return response.data;
  } catch (error) {
    console.error("Error saving insurance form:", error.message);
    throw new Error("Failed to save insurance form");
  }
};
