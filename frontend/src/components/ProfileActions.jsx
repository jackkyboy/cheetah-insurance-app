/*/Users/apichet/Downloads/cheetah-insurance-app/src/components/ProfileActions.jsx */

import React from "react";
import { useNavigate } from "react-router-dom";

const ProfileActions = ({
  handlePrepareInsuranceInfo,
  handleReportClaim,
  handleReviewInsurance,
}) => {
  const navigate = useNavigate();

  const handleGoToHome = () => {
    navigate("/");
  };

  return (
    <div className="profile-actions">
      <h3>เมนูเพิ่มเติม</h3>
      <div className="additional-actions">
        <button className="action-button" onClick={handlePrepareInsuranceInfo}>
          📋 เตรียมข้อมูลประกัน
        </button>
        <button className="action-button" onClick={handleReportClaim}>
          📄 แจ้งปัญหาเคลม
        </button>
        <button className="action-button" onClick={handleReviewInsurance}>
          ⭐ รีวิวประกันภัย
        </button>
        <button className="home-button" onClick={handleGoToHome}>
          🏠 กลับไปหน้าแรก
        </button>
      </div>
    </div>
  );
};

export default ProfileActions;
