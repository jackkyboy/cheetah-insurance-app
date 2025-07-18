// /Users/apichet/Downloads/cheetah-insurance-app/src/components/MessageBubble.jsx
// /src/components/MessageBubble.jsx
import React from "react";
import "../assets/styles/MessageBubble.css";

const MessageBubble = ({ sender, text = "", packages = [] }) => {
    const isUser = sender === "user";
    const iconClass = "material-symbols-rounded";
  
    const renderTextLines = (rawText) =>
      rawText
        .split("\n")
        .filter((line) => line.trim() !== "")
        .map((line, idx) => <p key={idx}>{line.trim()}</p>);
  
    const extractNetPremium = (pkg) =>
      pkg.premium_total ??
      pkg.net_premium ??
      pkg.package_data?.premium_total ??
      pkg.package_data?.net_premium ??
      pkg.coverage?.own_damage?.net_premium ??
      null;
  
    const extractInsuranceType = (pkg) =>
      pkg.insurance_type ??
      pkg.package_data?.insurance_type ??
      "ไม่ระบุ";
  
    const extractCompanyName = (pkg) =>
      pkg.insurance_company ??
      pkg.package_data?.insurance_company ??
      "ไม่ระบุ";
  
    const renderPackageCard = (pkg, idx) => {
      console.log("📦 DEBUG PACKAGE:", pkg); // ✅ Debug ตรงนี้
  
      const netPremium = extractNetPremium(pkg);
      const premiumText = typeof netPremium === "number"
        ? `${netPremium.toLocaleString()} บาท`
        : pkg.net_premium_range || "ไม่ระบุ";
  
      const insuranceType = extractInsuranceType(pkg);
      const companyName = extractCompanyName(pkg);
  
      return (
        <div key={idx} className="package-card">
          <strong>{companyName}</strong>
          <p>💰 <strong>เบี้ยสุทธิ:</strong> {premiumText}</p>
          <p>📋 <strong>ประเภท:</strong> {insuranceType}</p>
          {pkg.description && (
            <p className="pkg-desc">📝 {pkg.description}</p>
          )}
          {pkg.flagged_fake_price && (
            <p className="warning-text">⚠️ เบี้ยนี้อาจไม่ยืนยันจากระบบจริง</p>
          )}
        </div>
      );
    };
  
    return (
      <div className={`message ${isUser ? "outgoing" : "incoming"}`}>
        <div className="message-content">
          {!isUser && (
            <span className={`avatar icon ${iconClass}`}>smart_toy</span>
          )}
  
          <div className="bubble-content">
            {text.trim() && (
              <div className="text">{renderTextLines(text)}</div>
            )}
  
            {packages.length > 0 && (
              <div className="package-list">
                {packages.slice(0, 3).map(renderPackageCard)}
              </div>
            )}
          </div>
  
          {isUser && (
            <span className={`avatar icon ${iconClass}`}>person</span>
          )}
        </div>
      </div>
    );
  };
  
  export default MessageBubble;
  