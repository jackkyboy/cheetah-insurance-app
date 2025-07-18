import React, { useState } from "react";
import "../assets/styles/PolicyMockupForm.css"; // Ensure this file exists and is correctly linked

const PolicyMockupForm = () => {
  const [policyData, setPolicyData] = useState({
    ReferenceNo: "",
    agentCode: "",
    ProductCode: "",
    Campaign: "",
    PartnerCode: "",
    PolicyStatus: "N",
    EffectiveDate: "",
    ExpireDate: "",
    SumInsured: "",
    Premium: "",
    StampDuty: "",
    VAT: "",
    TotalPremium: "",
    DeliveryType: "",
    Coverage: "Y",
    Driver: "Y",
    Beneficiary: "Y",
    Insured: {
      TitleName: "",
      Name: "",
      Surname: "",
      IdNo: "",
      BirthDate: "",
      Nationality: "THA",
      AddressNo: "",
      Province: "",
      ZipCode: "",
      MobilePhone: "",
      EmailAddress: "",
    },
    MotorDetail: {
      Brand: "",
      Model: "",
      Registration: "",
      RegistrationProvince: "",
      ManufactureYear: "",
    },
  });

  const handleChange = (field, value, section = null) => {
    if (section) {
      setPolicyData((prev) => ({
        ...prev,
        [section]: {
          ...prev[section],
          [field]: value,
        },
      }));
    } else {
      setPolicyData((prev) => ({
        ...prev,
        [field]: value,
      }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Policy Data Submitted:", policyData);
    // API call to backend or mockup save can be added here
  };

  return (
    <form onSubmit={handleSubmit} className="policy-form-container">
      <h1>Mock Policy Form</h1>

      {/* Header */}
      <h2 className="section-header">Header</h2>
      <InputField
        label="Reference No:"
        value={policyData.ReferenceNo}
        onChange={(e) => handleChange("ReferenceNo", e.target.value)}
      />
      <InputField
        label="Agent Code:"
        value={policyData.agentCode}
        onChange={(e) => handleChange("agentCode", e.target.value)}
      />
      <SelectField
        label="Policy Status:"
        options={[
          { value: "N", label: "New" },
          { value: "R", label: "Renew" },
        ]}
        value={policyData.PolicyStatus}
        onChange={(e) => handleChange("PolicyStatus", e.target.value)}
      />
      <InputField
        label="Effective Date:"
        type="date"
        value={policyData.EffectiveDate}
        onChange={(e) => handleChange("EffectiveDate", e.target.value)}
      />
      <InputField
        label="Expire Date:"
        type="date"
        value={policyData.ExpireDate}
        onChange={(e) => handleChange("ExpireDate", e.target.value)}
      />
      <InputField
        label="Sum Insured:"
        type="number"
        value={policyData.SumInsured}
        onChange={(e) => handleChange("SumInsured", e.target.value)}
      />
      <InputField
        label="Premium:"
        type="number"
        value={policyData.Premium}
        onChange={(e) => handleChange("Premium", e.target.value)}
      />

      {/* Insured Information */}
      <h2 className="section-header">Insured Information</h2>
      <InputField
        label="Title Name:"
        value={policyData.Insured.TitleName}
        onChange={(e) => handleChange("TitleName", e.target.value, "Insured")}
      />
      <InputField
        label="Name:"
        value={policyData.Insured.Name}
        onChange={(e) => handleChange("Name", e.target.value, "Insured")}
      />
      <InputField
        label="Surname:"
        value={policyData.Insured.Surname}
        onChange={(e) => handleChange("Surname", e.target.value, "Insured")}
      />
      <InputField
        label="ID Number:"
        value={policyData.Insured.IdNo}
        onChange={(e) => handleChange("IdNo", e.target.value, "Insured")}
      />

      {/* Vehicle Information */}
      <h2 className="section-header">Vehicle Information</h2>
      <InputField
        label="Brand:"
        value={policyData.MotorDetail.Brand}
        onChange={(e) => handleChange("Brand", e.target.value, "MotorDetail")}
      />
      <InputField
        label="Model:"
        value={policyData.MotorDetail.Model}
        onChange={(e) => handleChange("Model", e.target.value, "MotorDetail")}
      />
      <InputField
        label="Manufacture Year:"
        type="number"
        value={policyData.MotorDetail.ManufactureYear}
        onChange={(e) =>
          handleChange("ManufactureYear", e.target.value, "MotorDetail")
        }
      />

      <button type="submit" className="submit-button">
        Submit Policy
      </button>
    </form>
  );
};

const InputField = ({ label, type = "text", value, onChange }) => (
  <label className="input-label">
    {label}
    <input type={type} value={value} onChange={onChange} className="input-field" />
  </label>
);

const SelectField = ({ label, options, value, onChange }) => (
  <label className="input-label">
    {label}
    <select value={value} onChange={onChange} className="input-field">
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  </label>
);

export default PolicyMockupForm;
