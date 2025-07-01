import React from "react";
import { useLocation, useNavigate } from "react-router-dom";

const PolicyConfirmation = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const policyData = location.state?.policyData;

  if (!policyData) {
    return <p>ไม่พบข้อมูลกรมธรรม์</p>;
  }

  return (
    <div style={{ padding: "20px", maxWidth: "800px", margin: "0 auto" }}>
      <h1 style={{ color: "#28a745", textAlign: "center" }}>สร้างกรมธรรม์สำเร็จ!</h1>
      <div style={{ marginTop: "20px", textAlign: "center", fontSize: "1.2rem" }}>
        <p>หมายเลขกรมธรรม์: {policyData.policyDetails?.ProposalID || "ไม่ระบุ"}</p>
        <p>บริษัทประกัน: {policyData.policyDetails?.company_name || "ไม่ระบุ"}</p>
      </div>
      <div style={{ display: "flex", justifyContent: "center", marginTop: "20px" }}>
        <button
          onClick={() => navigate("/")}
          style={{
            backgroundColor: "#007BFF",
            color: "#fff",
            padding: "10px 20px",
            borderRadius: "5px",
            border: "none",
          }}
        >
          กลับสู่หน้าหลัก
        </button>
      </div>
    </div>
  );
};

export default PolicyConfirmation;
