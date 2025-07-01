import React from "react";

const PolicyForm = () => {
  return (
    <form>
      <h2>ข้อมูลกรมธรรม์</h2>
      <label>ทุนประกัน:</label>
      <input type="number" name="sumInsured" placeholder="กรอกทุนประกัน" />
      <br />
      <label>เบี้ยประกัน:</label>
      <input type="number" name="premium" placeholder="กรอกเบี้ยประกัน" />
      <br />
      <label>วันที่เริ่มต้นคุ้มครอง:</label>
      <input type="date" name="effectiveDate" />
    </form>
  );
};

export default PolicyForm;
