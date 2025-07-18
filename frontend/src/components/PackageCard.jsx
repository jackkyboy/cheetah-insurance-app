///Users/apichet/Downloads/cheetah-insurance-app/src/components/PackageCard.jsx
///Users/apichet/Downloads/cheetah-insurance-app/src/components/PackageCard.jsx
import React, { useMemo } from "react";
import PropTypes from "prop-types";
import "../assets/styles/PackageCard.css";
import { COMPANY_INFO } from "../api/companyInfo";
import FieryInsuranceCard from "./FieryInsuranceCard"; // ✅ import มาใช้

const PackageCard = ({ pkg, onViewDetails, onViewFullDetails }) => {
  if (!pkg) return null;

  const sanitizeLogoUrl = (url) => {
    if (!url || url.includes("default-logo.svg")) {
      return "/logos/partners/default-logo.svg";
    }
    if (url.startsWith("http") || url.startsWith("data:")) return url;
    if (url.startsWith("/logos/")) return url;
    return `/logos/partners/${url}`;
  };

  const rawCompany = (pkg.insurance_company || pkg.company_name || "").toLowerCase().trim();
  const matchedKey = Object.keys(COMPANY_INFO).find((key) =>
    rawCompany.includes(key)
  );
  const company = matchedKey ? COMPANY_INFO[matchedKey] : null;

  const logoUrl = useMemo(() => sanitizeLogoUrl(company?.logo), [company]);

  const enrichedPkg = {
    ...pkg,
    insurance_company: pkg.insurance_company || pkg.company_name || "ไม่ระบุบริษัท",
    company_full_name: company?.name || pkg.company_name || pkg.insurance_company || "ไม่ระบุบริษัท",
    company_logo: logoUrl,
  };

  // ✅ 🔥 ใช้ FieryInsuranceCard กับทุกการ์ด
  return (
    <FieryInsuranceCard
      title={`ชั้น ${pkg.insurance_type || "-"} - ${enrichedPkg.company_full_name}`}
      price={pkg.premium ? parseFloat(pkg.premium).toLocaleString() : "N/A"}
      features={[
        `ยี่ห้อ: ${pkg.car_brand || "-"}`,
        `รุ่น: ${pkg.car_model || "-"}`,
        `ปี: ${pkg.car_model_year || "-"}`,
        `ซ่อม: ${pkg.repair_type || "-"}`,
      ]}
      onClick={() => onViewFullDetails?.(enrichedPkg)}
    />
  );
};

PackageCard.propTypes = {
  pkg: PropTypes.object,
  onViewDetails: PropTypes.func,
  onViewFullDetails: PropTypes.func,
};

export default PackageCard;
