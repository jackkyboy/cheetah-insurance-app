/*/Users/apichet/Downloads/cheetah-insurance-app/src/pages/InsuredForm.jsx */
import React from "react";
import { useFormState } from "../hooks/useFormState";

const InsuredForm = () => {
  const { formState, updateFormState } = useFormState();

  return (
    <div className="insured-form">
      <h2 className="form-title">ข้อมูลลูกค้า</h2>

      <div className="form-group">
        <label htmlFor="insuredName">ชื่อ:</label>
        <input
          id="insuredName"
          type="text"
          value={formState.insured?.name || ""}
          onChange={(e) => updateFormState("insured", "name", e.target.value)}
          placeholder="กรอกชื่อ"
          className="form-input"
        />
      </div>

      <div className="form-group">
        <label htmlFor="insuredSurname">นามสกุล:</label>
        <input
          id="insuredSurname"
          type="text"
          value={formState.insured?.surname || ""}
          onChange={(e) => updateFormState("insured", "surname", e.target.value)}
          placeholder="กรอกนามสกุล"
          className="form-input"
        />
      </div>

      <div className="form-group">
        <label htmlFor="insuredIdCard">เลขบัตรประชาชน:</label>
        <input
          id="insuredIdCard"
          type="text"
          value={formState.insured?.idCard || ""}
          onChange={(e) => updateFormState("insured", "idCard", e.target.value)}
          placeholder="กรอกเลขบัตรประชาชน"
          className="form-input"
        />
      </div>
    </div>
  );
};

export default InsuredForm;
