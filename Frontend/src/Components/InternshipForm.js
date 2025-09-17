import React, { useState } from "react";
import styles from "../styles/InternshipForm.module.css";

const InternshipForm = ({ onSubmit, loading }) => {
  const [education, setEducation] = useState("");
  const [skills, setSkills] = useState("");
  const [location, setLocation] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!education || !skills || !location) {
      setError("All fields are required.");
      return;
    }
    setError("");
    onSubmit(education, skills, location);
  };

  return (
    <form onSubmit={handleSubmit} className={styles.formContainer}>
      {error && <p className={styles.error}>{error}</p>}

      <div className={styles.inputGroup}>
        <label className={styles.label}>Education</label>
        <input
          type="text"
          value={education}
          onChange={(e) => setEducation(e.target.value)}
          className={styles.input}
          placeholder="e.g., B.Tech Computer Science"
        />
      </div>

      <div className={styles.inputGroup}>
        <label className={styles.label}>Skills (comma-separated)</label>
        <input
          type="text"
          value={skills}
          onChange={(e) => setSkills(e.target.value)}
          className={styles.input}
          placeholder="e.g., Python, FastAPI"
        />
      </div>

      <div className={styles.inputGroup}>
        <label className={styles.label}>Location</label>
        <input
          type="text"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          className={styles.input}
          placeholder="e.g., Pune"
        />
      </div>

      <button type="submit" disabled={loading} className={styles.button}>
        {loading ? "Loading..." : "Get Recommendations"}
      </button>
    </form>
  );
};

export default InternshipForm;
