import React, { useState } from "react";
import InternshipForm from "./components/InternshipForm";
import InternshipList from "./components/InternshipList";
import { getRecommendations } from "./services/api";
import styles from "./styles/App.module.css";

function App() {
  const [internships, setInternships] = useState([]);
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState("");

  const handleFormSubmit = async (education, skills, location) => {
    setLoading(true);
    setApiError("");
    try {
      const response = await getRecommendations(education, skills, location);
      setInternships(response.data.items || []);
    } catch (error) {
      setApiError(error.response?.data?.detail || "Failed to fetch recommendations.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.heading}>Internship Recommendation Engine</h1>
      <InternshipForm onSubmit={handleFormSubmit} loading={loading} />
      {apiError && <p style={{ color: "red" }}>{apiError}</p>}
      <InternshipList internships={internships} />
    </div>
  );
}

export default App;
