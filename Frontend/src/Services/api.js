// src/services/api.js
import axios from "axios";

// Base URL from environment variable
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

// POST request to /recommend endpoint
export const getRecommendations = async (education, skills, location) => {
  const payload = {
    education,
    skills: skills.split(",").map(s => s.trim()), // Convert comma-separated string to array
    location
  };
  return axios.post(`${API_BASE_URL}/recommend`, payload);
};
