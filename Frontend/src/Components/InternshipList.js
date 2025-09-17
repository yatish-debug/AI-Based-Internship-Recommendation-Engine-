// src/components/InternshipList.jsx
import React from "react";
import InternshipCard from "./InternshipCard";

const InternshipList = ({ internships }) => {
  if (!internships.length) {
    return <p className="text-gray-600">No recommendations yet.</p>;
  }

  return (
    <div className="mt-4">
      {internships.map((internship, index) => (
        <InternshipCard key={index} internship={internship} />
      ))}
    </div>
  );
};

export default InternshipList;
