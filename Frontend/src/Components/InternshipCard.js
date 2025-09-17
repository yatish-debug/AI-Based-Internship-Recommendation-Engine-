import React from "react";
import styles from "../styles/InternshipCard.module.css";

const InternshipCard = ({ internship }) => {
  return (
    <div className={styles.card}>
      <h3 className={styles.title}>{internship.title}</h3>
      <p className={styles.description}>{internship.description}</p>
      <p className={styles.meta}><strong>Location:</strong> {internship.location}</p>
      <p className={styles.meta}><strong>Duration:</strong> {internship.duration}</p>
    </div>
  );
};

export default InternshipCard;
