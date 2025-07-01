import React, { useState } from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import "../assets/styles/BrandDateTimePicker.css";

const CoverageDateTime = ({ onSave }) => {
  const now = new Date();
  const [startDate, setStartDate] = useState(now);
  const [startTime, setStartTime] = useState(
    `${now.getHours().toString().padStart(2, "0")}:${now.getMinutes()
      .toString()
      .padStart(2, "0")}`
  );

  const handleSave = () => {
    const formattedDate = startDate ? startDate.toISOString().split("T")[0] : "";
    const selectedTime = startTime || "";
    console.log("💾 [CoverageDateTime] Saving date and time:", {
      date: formattedDate,
      time: selectedTime,
    });
    onSave({ date: formattedDate, time: selectedTime });
  };

  return (
    <div className="app-container">
      <h3>📅 เลือกวันที่และเวลา</h3>

      <div className="datepicker-container">
        <label>เลือกวันที่:</label>
        <DatePicker
          selected={startDate}
          onChange={(date) => {
            console.log("📅 [CoverageDateTime] Date selected:", date);
            setStartDate(date);
          }}
          dateFormat="dd/MM/yyyy"
          minDate={new Date()}
          className="datepicker-input"
        />
      </div>

      <div className="timepicker-container">
        <label>เลือกเวลา:</label>
        <input
          type="time"
          value={startTime || ""}
          onChange={(e) => {
            console.log("⏰ [CoverageDateTime] Time selected:", e.target.value);
            setStartTime(e.target.value);
          }}
          className="timepicker-input"
        />
      </div>

      <div className="buttons-container">
        <button className="cancel-button" onClick={() => console.log("ยกเลิก")}>
          ยกเลิก
        </button>
        <button className="save-button" onClick={handleSave}>
          บันทึก
        </button>
      </div>
    </div>
  );
};

export default CoverageDateTime;
