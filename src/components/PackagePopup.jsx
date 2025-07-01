// /Users/apichet/Downloads/cheetah-insurance-app/src/components/PackagePopup.jsx
import React from "react";
import PropTypes from "prop-types";
import "../assets/styles/PackagePopup.css";

// Mapping สำหรับชื่อเต็มบริษัทในภาษาไทยและภาษาอังกฤษ
const getFullCompanyName = (shortName, lang = "th") => {
  const companyNameMapping = {
    "Tokio Marine": {
      th: "บริษัท คุ้มภัยโตเกียวมารีนประกันภัย (ประเทศไทย) จำกัด (มหาชน)",
      en: "Tokio Marine Insurance (Thailand) Public Company Limited",
    },
    "Ergo": {
      th: "บริษัท เออร์โกประกันภัย (ประเทศไทย) จำกัด (มหาชน)",
      en: "Ergo Insurance (Thailand) Public Company Limited",
    },
    "Chubb": {
      th: "บริษัท ชับบ์สามัคคีประกันภัย จำกัด (มหาชน)",
      en: "Chubb Samaggi Insurance Public Company Limited",
    },
    "Viriyah": {
      th: "บริษัท วิริยะประกันภัย จำกัด (มหาชน)",
      en: "Viriyah Insurance Public Company Limited",
    },
    "MSIG": {
      th: "บริษัท เอ็มเอสไอ ประกันภัย (ประเทศไทย) จำกัด (มหาชน)",
      en: "MSIG Insurance (Thailand) Public Company Limited",
    },
    "MTI": {
      th: "บริษัท เมืองไทยประกันภัย จำกัด (มหาชน)",
      en: "Muang Thai Insurance Public Company Limited",
    },
  };

  return companyNameMapping[shortName]?.[lang] || shortName;
};

const PackagePopup = ({ packageData, onClose, lang = "th" }) => {
  if (!packageData) {
    return null; // หาก packageData ไม่มีข้อมูล ไม่แสดง Popup
  }

  const fullCompanyName = getFullCompanyName(packageData.company_name, lang);

  return (
    <div
      className="popup-overlay"
      role="dialog"
      aria-labelledby="popup-title"
      aria-describedby="popup-description"
    >
      <div className="popup-content">
        <h3 id="popup-title">ตารางความคุ้มครอง พ.ร.บ.</h3>
        <p id="popup-description">
          <strong>บริษัท:</strong> {fullCompanyName}
        </p>
        <table className="coverage-table">
          <thead>
            <tr>
              <th>ความคุ้มครอง</th>
              <th>จำนวนเงิน (บาท)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>1.1 บาดเจ็บ (ค่ารักษาพยาบาล)</td>
              <td>30,000 บาท/คน</td>
            </tr>
            <tr>
              <td>1.2 เสียชีวิต (ค่าปลงศพ)</td>
              <td>35,000 บาท/คน</td>
            </tr>
            <tr>
              <td>1.3 รวมค่ารักษาพยาบาล + ค่าปลงศพ</td>
              <td>65,000 บาท/คน</td>
            </tr>
            <tr>
              <td>2.1 กรณีเสียชีวิตสูงสุด</td>
              <td>500,000 บาท/คน</td>
            </tr>
            <tr>
              <td>2.3 ค่ารักษาพยาบาล (ไม่เกิน)</td>
              <td>80,000 บาท/คน</td>
            </tr>
            <tr>
              <td>2.5 วงเงินสูงสุดต่อคน</td>
              <td>504,000 บาท/คน</td>
            </tr>
          </tbody>
        </table>
        <div className="popup-actions">
          <button
            className="close-btn"
            onClick={onClose}
            aria-label="ปิดหน้าต่างป๊อปอัพ"
          >
            ปิด
          </button>
        </div>
      </div>
    </div>
  );
};

// ตรวจสอบ props ที่ส่งเข้ามา
PackagePopup.propTypes = {
  packageData: PropTypes.shape({
    company_name: PropTypes.string,
  }),
  onClose: PropTypes.func.isRequired,
  lang: PropTypes.oneOf(["th", "en"]),
};

// ค่าเริ่มต้นสำหรับ props
PackagePopup.defaultProps = {
  packageData: null,
  lang: "th",
};

export default PackagePopup;
