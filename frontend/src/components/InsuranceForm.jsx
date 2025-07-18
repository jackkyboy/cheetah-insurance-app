import React, { useState } from "react";
import { useNavigate } from "react-router-dom"; // สำหรับเปลี่ยนหน้า
import "../assets/styles/InsuranceForm.css";

const InsuranceForm = () => {
  const [formData, setFormData] = useState({
    insured: {
      title: "",
      firstName: "",
      lastName: "",
      idNumber: "",
      birthDate: "",
      age: "",
      mobile: "",
      email: "",
    },
    address: {
      homeNo: "",
      moo: "",
      mooBarn: "",
      soi: "",
      road: "",
      tambol: "",
      amphur: "",
      province: "",
      zipCode: "",
    },
    invoice: {
      title: "",
      firstName: "",
      lastName: "",
      homeNo: "",
      moo: "",
      mooBarn: "",
      soi: "",
      road: "",
      tambol: "",
      amphur: "",
      province: "",
      zipCode: "",
    },
    beneficiary: {
      name: "",
      relationship: "",
    },
    vehicle: {
      licenseNo: "",
      licenseProvince: "",
      chassisNo: "",
      engineNo: "",
      make: "",
      spec: "",
      model: "",
      modelYear: "",
      registrationYear: "",
      cc: "",
      seat: "",
      weight: "",
    },
    policy: {
      packageCode: "",
      voluntaryClassCode: "",
      voluntaryClassName: "",
      voluntaryCode: "",
      policyType: "",
      coverOD: "",
      netGrossPremium: "",
      duty: "",
      tax: "",
      totalPremium: "",
      isTakaful: "N",
      isMuslim: "N",
    },
    driver: {
      driverTypeFlag: "N",
      driverAmount: 0,
      driver1: {
        title: "",
        firstName: "",
        lastName: "",
        birthDate: "",
        age: "",
        idNumber: "",
        licenseNo: "",
      },
      driver2: {
        title: "",
        firstName: "",
        lastName: "",
        birthDate: "",
        age: "",
        idNumber: "",
        licenseNo: "",
      },
    },
  });

  const [visibleSections, setVisibleSections] = useState({
    insured: true,
    address: false,
    invoice: false,
    beneficiary: false,
    vehicle: false,
    policy: false,
    driver: false,
  });

  const navigate = useNavigate(); // ใช้สำหรับเปลี่ยนหน้า

  const toggleSection = (section) => {
    setVisibleSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const handleInputChange = (e, section, key) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key || name]: value,
      },
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Form submitted:", formData);
    alert("🎉 บันทึกข้อมูลสำเร็จ!");
  };

  const handleViewDocument = () => {
    // ส่งข้อมูลไปยัง PolicyDocument.jsx
    navigate("/policy-document", { state: { formData } });
  };

  return (
    <div className="insurance-form">
      <h1>กรอกข้อมูลเพื่อออกกรมธรรม์</h1>
      <form onSubmit={handleSubmit}>
        {/* Section: ผู้เอาประกัน */}
        <section>
          <h2 onClick={() => toggleSection("insured")} className="section-header">
            ข้อมูลผู้เอาประกัน {visibleSections.insured ? "▲" : "▼"}
          </h2>
          {visibleSections.insured && (
            <div className="form-grid">
              <label>
                คำนำหน้า:
                <input
                  type="text"
                  name="title"
                  value={formData.insured.title}
                  onChange={(e) => handleInputChange(e, "insured", "title")}
                />
              </label>
              <label>
                ชื่อ:
                <input
                  type="text"
                  name="firstName"
                  value={formData.insured.firstName}
                  onChange={(e) => handleInputChange(e, "insured", "firstName")}
                />
              </label>
              <label>
                นามสกุล:
                <input
                  type="text"
                  name="lastName"
                  value={formData.insured.lastName}
                  onChange={(e) => handleInputChange(e, "insured", "lastName")}
                />
              </label>
              <label>
                หมายเลขบัตรประชาชน:
                <input
                  type="text"
                  name="idNumber"
                  value={formData.insured.idNumber}
                  onChange={(e) => handleInputChange(e, "insured", "idNumber")}
                />
              </label>
            </div>
          )}
        </section>
  
        {/* Section: ที่อยู่ */}
        <section>
          <h2 onClick={() => toggleSection("address")} className="section-header">
            ที่อยู่ {visibleSections.address ? "▲" : "▼"}
          </h2>
          {visibleSections.address && (
            <div className="form-grid">
              <label>
                บ้านเลขที่:
                <input
                  type="text"
                  name="homeNo"
                  value={formData.address.homeNo}
                  onChange={(e) => handleInputChange(e, "address", "homeNo")}
                />
              </label>
              <label>
                หมู่:
                <input
                  type="text"
                  name="moo"
                  value={formData.address.moo}
                  onChange={(e) => handleInputChange(e, "address", "moo")}
                />
              </label>
              <label>
                หมู่บ้าน:
                <input
                  type="text"
                  name="mooBarn"
                  value={formData.address.mooBarn}
                  onChange={(e) => handleInputChange(e, "address", "mooBarn")}
                />
              </label>
              <label>
                ซอย:
                <input
                  type="text"
                  name="soi"
                  value={formData.address.soi}
                  onChange={(e) => handleInputChange(e, "address", "soi")}
                />
              </label>
              <label>
                ถนน:
                <input
                  type="text"
                  name="road"
                  value={formData.address.road}
                  onChange={(e) => handleInputChange(e, "address", "road")}
                />
              </label>
              <label>
                ตำบล:
                <input
                  type="text"
                  name="tambol"
                  value={formData.address.tambol}
                  onChange={(e) => handleInputChange(e, "address", "tambol")}
                />
              </label>
              <label>
                อำเภอ:
                <input
                  type="text"
                  name="amphur"
                  value={formData.address.amphur}
                  onChange={(e) => handleInputChange(e, "address", "amphur")}
                />
              </label>
              <label>
                จังหวัด:
                <input
                  type="text"
                  name="province"
                  value={formData.address.province}
                  onChange={(e) => handleInputChange(e, "address", "province")}
                />
              </label>
              <label>
                รหัสไปรษณีย์:
                <input
                  type="text"
                  name="zipCode"
                  value={formData.address.zipCode}
                  onChange={(e) => handleInputChange(e, "address", "zipCode")}
                />
              </label>
            </div>
          )}
        </section>
  
        {/* Section: ผู้รับผลประโยชน์ */}
        <section>
          <h2 onClick={() => toggleSection("beneficiary")} className="section-header">
            ข้อมูลผู้รับผลประโยชน์ {visibleSections.beneficiary ? "▲" : "▼"}
          </h2>
          {visibleSections.beneficiary && (
            <div className="form-grid">
              <label>
                ชื่อผู้รับผลประโยชน์:
                <input
                  type="text"
                  name="name"
                  value={formData.beneficiary.name}
                  onChange={(e) => handleInputChange(e, "beneficiary", "name")}
                />
              </label>
              <label>
                ความสัมพันธ์:
                <input
                  type="text"
                  name="relationship"
                  value={formData.beneficiary.relationship}
                  onChange={(e) =>
                    handleInputChange(e, "beneficiary", "relationship")
                  }
                />
              </label>
            </div>
          )}
        </section>
  
        {/* Section: รถยนต์ */}
        <section>
          <h2 onClick={() => toggleSection("vehicle")} className="section-header">
            ข้อมูลรถยนต์ {visibleSections.vehicle ? "▲" : "▼"}
          </h2>
          {visibleSections.vehicle && (
            <div className="form-grid">
              <label>
                เลขทะเบียนรถ:
                <input
                  type="text"
                  name="licenseNo"
                  value={formData.vehicle.licenseNo}
                  onChange={(e) => handleInputChange(e, "vehicle", "licenseNo")}
                />
              </label>
              <label>
                จังหวัดที่จดทะเบียน:
                <input
                  type="text"
                  name="licenseProvince"
                  value={formData.vehicle.licenseProvince}
                  onChange={(e) =>
                    handleInputChange(e, "vehicle", "licenseProvince")
                  }
                />
              </label>
              <label>
                ยี่ห้อรถ:
                <input
                  type="text"
                  name="make"
                  value={formData.vehicle.make}
                  onChange={(e) => handleInputChange(e, "vehicle", "make")}
                />
              </label>
              <label>
                รุ่นรถ:
                <input
                  type="text"
                  name="model"
                  value={formData.vehicle.model}
                  onChange={(e) => handleInputChange(e, "vehicle", "model")}
                />
              </label>
            </div>
          )}
        </section>
  
        {/* Section: กรมธรรม์ */}
        <section>
          <h2 onClick={() => toggleSection("policy")} className="section-header">
            ข้อมูลกรมธรรม์ {visibleSections.policy ? "▲" : "▼"}
          </h2>
          {visibleSections.policy && (
            <div className="form-grid">
              <label>
                รหัสแพคเกจ:
                <input
                  type="text"
                  name="packageCode"
                  value={formData.policy.packageCode}
                  onChange={(e) => handleInputChange(e, "policy", "packageCode")}
                />
              </label>
              <label>
                เบี้ยประกันภัยรวม:
                <input
                  type="text"
                  name="totalPremium"
                  value={formData.policy.totalPremium}
                  onChange={(e) =>
                    handleInputChange(e, "policy", "totalPremium")
                  }
                />
              </label>
            </div>
          )}
        </section>
  
        <div className="form-actions">
          <button type="submit" className="submit-btn">
            บันทึกข้อมูล
          </button>

          {/* ปุ่มดูเอกสาร */}
          <button
            type="button"
            className="submit-btn"
            style={{ backgroundColor: "#FF6800", marginTop: "10px" }}
            onClick={handleViewDocument}
          >
            ดูเอกสาร
          </button>
        </div>
      </form>
    </div>
  );
};


export default InsuranceForm;
