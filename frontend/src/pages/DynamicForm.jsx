import React, { useState } from "react";
import InsuredForm from "./InsuredForm";
import MotorForm from "./MotorForm";
import PolicyForm from "../components/PolicyForm";
import DriverForm from "./DriverForm";
import BeneficiaryForm from "./BeneficiaryForm";

// Define sections with their IDs and titles
const sections = [
  { id: "insured", title: "ข้อมูลลูกค้า" },
  { id: "motor", title: "ข้อมูลรถยนต์" },
  { id: "policy", title: "ข้อมูลกรมธรรม์" },
  { id: "drivers", title: "ข้อมูลผู้ขับขี่" },
  { id: "beneficiaries", title: "ข้อมูลผู้รับผลประโยชน์" },
];

const DynamicForm = () => {
  const [activeSection, setActiveSection] = useState("insured"); // Track the active section

  // Dynamically render the active section based on the selected tab
  const renderSection = () => {
    switch (activeSection) {
      case "insured":
        return <InsuredForm />;
      case "motor":
        return <MotorForm />;
      case "policy":
        return <PolicyForm />;
      case "drivers":
        return <DriverForm />;
      case "beneficiaries":
        return <BeneficiaryForm />;
      default:
        return null;
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>เตรียมข้อมูลสำหรับประกันภัย</h1>
      {/* Section navigation buttons */}
      <div style={{ display: "flex", flexWrap: "wrap", marginBottom: "20px" }}>
        {sections.map((section) => (
          <button
            key={section.id}
            onClick={() => setActiveSection(section.id)}
            style={{
              margin: "5px",
              padding: "10px 20px",
              backgroundColor: activeSection === section.id ? "#007BFF" : "#CCC",
              color: "#FFF",
              border: "none",
              borderRadius: "5px",
              cursor: "pointer",
            }}
          >
            {section.title}
          </button>
        ))}
      </div>
      {/* Render the form content of the selected section */}
      <div style={{ marginTop: "20px" }}>{renderSection()}</div>
    </div>
  );
};

export default DynamicForm;
