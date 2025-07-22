/*/Users/apichet/Downloads/cheetah-insurance-app/src/components/PackageDetails.jsx*/
import React, { useState, useEffect } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import "../assets/styles/PackageDetails.css";
import InfoTooltip from "./InfoTooltip";
import { getCarLogoUrl } from "../api/carLogos"; // ตรวจสอบ path ว่าถูกต้อง
import PartnerAddOns from "./PartnerAddOns";
import CoverageDateTime from "./CoverageDateTime";
import { jwtDecode } from "jwt-decode"; // Correct
import "../assets/styles/animatedGradientText.css";


// Mapping สำหรับชื่อเต็มบริษัทในภาษาไทยและภาษาอังกฤษ
// ฟังก์ชันสำหรับดึงชื่อเต็มบริษัท
const getFullCompanyName = (shortName, lang = "th") => {
  if (!shortName || typeof shortName !== "string") return "ไม่ระบุบริษัท";

  // ✅ ย้าย mapping และ aliases มาไว้ด้านบนก่อนใช้งาน
  const mapping = {
    chubb: {
      th: "บริษัท ชับบ์สามัคคีประกันภัย จำกัด (มหาชน)",
      en: "Chubb Samaggi Insurance Public Company Limited",
    },
    ergo: {
      th: "บริษัท เออร์โกประกันภัย (ประเทศไทย) จำกัด (มหาชน)",
      en: "Ergo Insurance (Thailand) Public Company Limited",
    },
    mti: {
      th: "บริษัท เมืองไทยประกันภัย จำกัด (มหาชน)",
      en: "Muang Thai Insurance Public Company Limited",
    },
    viriyah: {
      th: "บริษัท วิริยะประกันภัย จำกัด (มหาชน)",
      en: "Viriyah Insurance Public Company Limited",
    },
    tokiomarine: {
      th: "บริษัท คุ้มภัยโตเกียวมารีนประกันภัย (ประเทศไทย) จำกัด (มหาชน)",
      en: "Tokio Marine Insurance (Thailand) Public Company Limited",
    },
    msig: {
      th: "บริษัท เอ็มเอสไอ ประกันภัย (ประเทศไทย) จำกัด (มหาชน)",
      en: "MSIG Insurance (Thailand) Public Company Limited",
    },
  };

  const aliases = {
    chubb: ["chubb", "chubbsamaggi", "chubb samaggi insurance"],
    ergo: ["ergo"],
    mti: ["mti", "muangthai"],
    viriyah: ["viriyah", "viriyah insurance"],
    tokiomarine: ["tokio", "tokio marine", "tokio marine insurance"],
    msig: ["msig"],
  };

  const normalized = shortName.toLowerCase().replace(/[\s\-().]/g, "");

  const exactThaiMap = {
    "ชับบ์": "chubb",
    "เออร์โก": "ergo",
    "เมืองไทย": "mti",
    "วิริยะ": "viriyah",
    "โตเกียวมารีน": "tokiomarine",
    "เอ็มเอสไอจี": "msig",
    "เอ็มเอสไอ": "msig",
  };

  const fallbackKeyFromThai = exactThaiMap[shortName.trim()];
  if (fallbackKeyFromThai) {
    return mapping[fallbackKeyFromThai]?.[lang] || "ไม่ระบุบริษัท";
  }

  const key = Object.entries(aliases).find(([_, values]) =>
    values.some((alias) => normalized.includes(alias))
  )?.[0];

  return key ? mapping[key][lang] : "ไม่ระบุบริษัท";
};




const PackageDetail = () => {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  
  // ใช้ package_code จาก state ถ้าไม่มี id ใน URL
  const packageDataFromState = location.state?.packageData || null;
  const packageId = id ?? packageDataFromState?.package_code ?? null;
  
  console.log("📌 Package ID (final):", packageId);
  console.log("📌 Location State:", location.state);
  
  
  
 

  const [packageData, setPackageData] = useState(location.state?.packageData || null);
  const [logoUrl, setLogoUrl] = useState(location.state?.packageData?.company_logo || null); // ✅ ใช้ company_logo
  const [includeCmi, setIncludeCmi] = useState(false);
  const [totalPrice, setTotalPrice] = useState(null);
  const [loading, setLoading] = useState(!packageData);
  const [loadingPurchase, setLoadingPurchase] = useState(false);
  const [error, setError] = useState(null);
  const [calculation, setCalculation] = useState({});
  const [coverageDateTime, setCoverageDateTime] = useState({ date: "", time: "" });
  
  const [partnerAddOns] = useState([
    { id: 1, name: "ClaimDi", description: "ประกันอุบัติเหตุฉุกเฉิน", price: 300 },
    { id: 2, name: "AsiaCare", description: "ประกันภัยเครื่องยนต์", price: 500 },
  ]);
  const [selectedAddOns, setSelectedAddOns] = useState([]);
  const [coupons] = useState([{ id: 1, code: "DISCOUNT50", discount: 50 }]);
  const [appliedCoupon, setAppliedCoupon] = useState(null);
  
  const handleCoverageDateTimeSave = (data) => {
    setCoverageDateTime(data);
  };
  
  const insuranceTypeMapping = {
    "1": "ชั้น 1",
    "2": "ชั้น 2",
    "2+": "ชั้น 2+",
    "3": "ชั้น 3",
    "3+": "ชั้น 3+",
    "3P": "ชั้น 3P",
    "0": "ไม่มีประเภท",
  };
  
  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:5000/api";
  const BACKEND_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:5000";
  
  const sanitizeLogoUrl = (url) => {
    const fallbackPath = "/gallery_logos/partners/default-logo.svg";
  
    if (!url || typeof url !== "string" || url.trim() === "" || url.includes("default-logo.svg")) {
      return `${BACKEND_BASE_URL}${fallbackPath}`;
    }
  
    // ตรวจสอบว่าเป็น absolute URL หรือไม่
    return url.startsWith("http") ? url : `${BACKEND_BASE_URL}${url}`;
  };
  
  
  // 🎯 ดึงข้อมูล package ถ้ายังไม่มี
  useEffect(() => {
    if (!packageData) {
      fetchPackageData();
    } else {
      calculateTotalPrice(packageData); // คำนวณเบี้ย
    }
  }, [packageData, includeCmi, selectedAddOns, appliedCoupon]);
  
  // 🎯 ดึงโลโก้ถ้ายังไม่มีใน state
  useEffect(() => {
    if (!logoUrl && packageData?.insurance_company) {
      fetchLogo(packageData.insurance_company);
    }
  }, [logoUrl, packageData]);
  
  // ✅ โหลดแพ็กเกจจาก backend
  const fetchPackageData = async () => {
    try {
      if (!packageId) {
        setError("❌ ไม่พบรหัสแพ็กเกจ กรุณาลองใหม่");
        return;
      }
      setLoading(true);
      const res = await fetch(`${API_BASE_URL}/packages/${packageId}`);
      if (!res.ok) throw new Error("ไม่สามารถโหลดข้อมูลแพ็กเกจได้");
  
      const data = await res.json();
      setPackageData(data);
    } catch (err) {
      setError("❌ ไม่พบข้อมูลแพ็กเกจ กรุณากลับไปเลือกแพ็กเกจใหม่");
    } finally {
      setLoading(false);
    }
  };
  
  // ✅ ฟังก์ชันดึง logo ตามชื่อบริษัท
  const fetchLogo = async (companyName) => {
    try {
      const res = await fetch(`${API_BASE_URL}/car-options/packages_with_logos`);
      if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
      const data = await res.json();
  
      const logoMap = data.results.reduce((map, item) => {
        const key = item.insurance_company?.toLowerCase()?.replace(/\s+/g, "") || "";
        map[key] = sanitizeLogoUrl(item.logo_url);
        return map;
      }, {});
  
      const key = companyName?.toLowerCase()?.replace(/\s+/g, "");
      setLogoUrl(logoMap[key] || sanitizeLogoUrl(null));
    } catch (err) {
      console.error("❌ Error fetching logo:", err.message);
      setLogoUrl(sanitizeLogoUrl(null));
    }
  };
  
  



  // ฟังก์ชันคำนวณราคาสุทธิทั้งหมด
// ฟังก์ชันคำนวณราคาสุทธิทั้งหมด
const calculateTotalPrice = (data) => {
  try {
    console.log("🔄 เริ่มการคำนวณราคาสุทธิ...");

    if (!data) {
      throw new Error("ไม่มีข้อมูลแพ็กเกจที่ส่งเข้ามา");
    }

    const premium = parseFloat(data?.premium || 0); // เบี้ยประกัน
    console.log("💵 เบี้ยประกัน:", premium);

    const duty = Math.ceil(premium * 0.0004); // อากรแสตมป์
    console.log("🧾 อากรแสตมป์:", duty);

    const totalBeforeVat = premium + duty; // รวมก่อน VAT
    console.log("📊 รวมก่อน VAT:", totalBeforeVat);

    const vat = totalBeforeVat * 0.07; // VAT 7%
    console.log("💡 VAT (7%):", vat);

    // ✅ กำหนดค่า `addOnTotal` ให้เป็น 0 ถ้าไม่มีการเลือก Add-ons
    const addOnTotal = selectedAddOns.length > 0 
      ? selectedAddOns.reduce((sum, addOnId) => {
          const addOn = partnerAddOns.find((item) => item.id === addOnId);
          return sum + (addOn ? addOn.price : 0);
        }, 0)
      : 0;

    console.log("➕ ค่า Add-Ons:", addOnTotal);

    const couponDiscount = appliedCoupon ? appliedCoupon.discount : 0;
    console.log("🎟️ ส่วนลดจากคูปอง:", couponDiscount);

    const totalWithVat = totalBeforeVat + vat + addOnTotal - couponDiscount;
    console.log("💰 รวมราคาสุทธิ (ไม่รวมค่า พรบ.):", totalWithVat);

    const cmiAmount = includeCmi ? parseFloat(data?.coverage?.cmi_amount || 0) : 0; 
    console.log("🔖 ค่า พรบ.:", cmiAmount);

    const finalTotal = totalWithVat + cmiAmount;
    console.log("✅ ราคาสุทธิทั้งหมด:", finalTotal);

    setCalculation({
      premium,
      duty,
      totalBeforeVat,
      vat,
      addOnTotal, // ✅ เพิ่ม `addOnTotal`
      couponDiscount,
      totalWithVat,
      totalFinal: finalTotal,
    });

    setTotalPrice(finalTotal);
  } catch (error) {
    console.error("❌ Error during calculation:", error.message);
    setError("เกิดข้อผิดพลาดในการคำนวณ กรุณาลองใหม่อีกครั้ง");
  }
};

  
  

  // ฟังก์ชันดึงข้อมูลลูกค้าจาก API
  const fetchCustomerInfo = async () => {
    try {
      const authToken = localStorage.getItem("authToken");
      console.log("🔑 [fetchCustomerInfo] Token from localStorage:", authToken);
      if (!authToken) {
        alert("Session หมดอายุ กรุณาเข้าสู่ระบบใหม่");
        console.error("❌ [fetchCustomerInfo] Missing authToken");
        throw new Error("Unauthorized: Missing authToken");
      }
  
      console.log("📡 [fetchCustomerInfo] Fetching customer info...");
      const response = await fetch(`${API_BASE_URL}/user/customers/me`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });
  
      console.log("🌐 [fetchCustomerInfo] Response Status:", response.status);
  
      if (response.status === 401) {
        alert("Session หมดอายุ กรุณาเข้าสู่ระบบใหม่");
        localStorage.removeItem("authToken");
        localStorage.removeItem("refreshToken");
        sessionStorage.clear();
        console.error("❌ [fetchCustomerInfo] Unauthorized: Token expired or invalid");
        window.location.href = "/login";
        throw new Error("Unauthorized: Token expired or invalid");
      }
  
      if (!response.ok) {
        console.error("❌ [fetchCustomerInfo] Failed to fetch customer info. Response:", response);
        throw new Error("Failed to fetch customer info");
      }
  
      const customerData = await response.json();
      console.log("✅ [fetchCustomerInfo] Customer data fetched successfully:", customerData);
      sessionStorage.setItem("customerData", JSON.stringify(customerData));
      return customerData;
    } catch (error) {
      console.error("❌ [fetchCustomerInfo] Error fetching customer info:", error.message);
      throw error;
    }
  };


  
  const handlePurchase = async () => {
    console.log("🚀 [handlePurchase] Function started");
    setLoadingPurchase(true);
  
    try {
      console.log("🔍 Step 1: Checking for auth token");
      const authToken = localStorage.getItem("authToken");
      if (!authToken) {
        alert("กรุณาเข้าสู่ระบบใหม่");
        navigate("/login");
        return;
      }
  
      console.log("📡 Step 2: Fetching customer data");
      const customerData = await fetchCustomerInfo();
      if (!customerData?.customer_id) {
        alert("ข้อมูลลูกค้าไม่ถูกต้อง");
        navigate("/login");
        return;
      }
  
      console.log("📦 Step 3: Preparing payload with createPayload()");
      const payload = createPayload(customerData);
      console.log("📦 Payload:", payload);
  
      console.log("🌐 Step 4: Sending payment request...");
      const response = await fetch(`${API_BASE_URL}/payments/create`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${authToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
  
      console.log("🌐 Step 5: Handling API response...");
      await handleApiResponse(response);
    } catch (err) {
      console.error("❌ [handlePurchase] Unexpected Error:", err.message);
      alert(`เกิดข้อผิดพลาด: ${err.message}`);
    } finally {
      setLoadingPurchase(false);
      console.log("🔄 Purchase process completed");
    }
  };
  
  
  
  
  // ฟังก์ชันสำหรับสร้าง Payload
  // ฟังก์ชันสำหรับสร้าง Payload
  const createPayload = (customerData) => {
    try {
      if (!customerData?.customer_id) throw new Error("Customer ID is missing.");
      if (!id || typeof id !== "string") throw new Error("Package ID is missing or invalid.");
      if (!totalPrice || totalPrice <= 0) throw new Error("Invalid total price.");
  
      const premium = calculation?.premium ?? packageData?.premium;
      const duty = calculation?.duty;
      const vat = calculation?.vat;
      if ([premium, duty, vat].some((v) => v == null)) {
        throw new Error("Premium / Duty / VAT are missing.");
      }
  
      const { date, time } = coverageDateTime || {};
      if (!date || !time) throw new Error("Coverage date/time is missing.");
  
      const payload = {
        customer_id: customerData.customer_id,
        package_id: id,
        amount: totalPrice,
        currency: "THB",
        add_ons: selectedAddOns ?? [],
        coupon_code: appliedCoupon?.code ?? null,
        insurance_type: packageData?.insurance_type ?? null,
        insurance_company: packageData?.insurance_company ?? null,
        premium,
        duty,
        vat,
        car_brand: packageData?.car_brand ?? null,
        car_model: packageData?.car_model ?? null,
        car_submodel: packageData?.car_submodel ?? null,
        car_year: packageData?.car_year ?? null,
        coverage_start_date: date,
        coverage_start_time: time,
        description: "Insurance payment",
      };
  
      console.log("✅ [createPayload] Payload created:", payload);
      return payload;
    } catch (error) {
      console.error("❌ [createPayload]", error.message);
      alert(`เกิดข้อผิดพลาด: ${error.message}`);
      throw error;
    }
  };
  

  const handleApiResponse = async (response) => {
    try {
      if (!response) throw new Error("ไม่มีการตอบกลับจาก API");
  
      console.log("📦 [handleApiResponse] Response object:", response);
      console.log("📦 [handleApiResponse] Status:", response.status);
  
      let data;
      try {
        data = await response.json();
      } catch (jsonErr) {
        console.error("❌ [JSON Parsing Error]", jsonErr);
        throw new Error("ไม่สามารถแปลงข้อมูลเป็น JSON ได้");
      }
  
      console.log("✅ [Parsed JSON from response]:", data);
  
      if (!response.ok) {
        console.error("❌ [API Error]", data);
        alert(data?.error || "ไม่สามารถสร้างคำสั่งซื้อได้");
        return;
      }
  
      // ✅ ปรับให้รองรับ payload ซ้อน
      const token =
        typeof data?.payload === "string"
          ? data.payload
          : typeof data?.payload?.payload === "string"
          ? data.payload.payload
          : data?.payload;
  
      console.log("🧪 typeof token:", typeof token, "value:", token);
      window.__debug_token = token;
  
      if (!token) throw new Error("ไม่พบ payload จากเซิร์ฟเวอร์");
  
      // ✅ ถ้า payload เป็น object
      if (typeof token === "object") {
        console.log("🧩 [Token is object]:", token);
        console.log("📦 FULL OBJECT payload:", JSON.stringify(token, null, 2));
  
        const webUrl = [
          token?.redirect,
          token?.payment_url,
          token?.url,
          token?.webPaymentUrl,
          token?.web_payment_url,
          token?.webpaymenturl,
          token?.data?.redirect,
          token?.data?.webPaymentUrl,
          token?.data?.web_payment_url,
          token?.result?.redirect,
          token?.result?.webPaymentUrl
        ].find(url => typeof url === "string" && url.startsWith("http"));
  
        console.log("🌐 [Extracted URL from object]:", webUrl);
  
        if (webUrl) {
          console.log("🚀 Redirecting to (object):", webUrl);
          return (window.location.href = webUrl);
        } else {
          throw new Error("webPaymentUrl ไม่ถูกต้องหรือไม่พบใน token object");
        }
      }
  
      // ✅ ถ้า payload เป็น JWT string
      if (typeof token === "string" && token.length > 20) {
        console.log("🔐 [Token is JWT string]:", token);
  
        let decoded;
        try {
          decoded = jwtDecode(token);
          console.log("🔓 [Decoded JWT]:", decoded);
          console.log("📦 FULL DECODED JWT:", JSON.stringify(decoded, null, 2));
          window.__debug_decoded = decoded;
        } catch (err) {
          console.error("❌ [JWT Decode Error]:", err);
          throw new Error("ไม่สามารถถอดรหัส token ได้");
        }
  
        const webPaymentUrl = [
          decoded?.redirect,
          decoded?.payment_url,
          decoded?.url,
          decoded?.webPaymentUrl,
          decoded?.web_payment_url,
          decoded?.webpaymenturl,
          decoded?.data?.webPaymentUrl,
          decoded?.data?.web_payment_url,
          decoded?.data?.redirect
        ].find(url => typeof url === "string" && url.startsWith("http"));
  
        console.log("🌐 [Extracted URL from decoded JWT]:", webPaymentUrl);
  
        if (webPaymentUrl) {
          console.log("🚀 Redirecting to (JWT):", webPaymentUrl);
          return (window.location.href = webPaymentUrl);
        } else {
          throw new Error("webPaymentUrl ไม่ถูกต้องหรือไม่พบใน decoded JWT");
        }
      }
  
      throw new Error("Token ไม่ถูกต้องหรือไม่สามารถถอดรหัสได้");
  
    } catch (err) {
      console.error("❌ [handleApiResponse Catch Block]", err.message);
      alert(`เกิดข้อผิดพลาด: ${err.message}`);
    }
  };
  
  
  
  
  
  
  

  
  
  
  
  
  
  
  


      
  // ✅ ฟังก์ชันที่ปรับใหม่ — รองรับ 0, null, undefined, string
  const renderCoverageDetail = (label, value, tooltipTitle, tooltipDescription) => {
    let displayValue = "ไม่ระบุ";

    if (typeof value === "number") {
      displayValue = value.toLocaleString(); // เช่น 1000000 -> 1,000,000
    } else if (typeof value === "string" && value.trim() !== "") {
      displayValue = value;
    }

    return (
      <li>
        <strong>
          {label} <InfoTooltip title={tooltipTitle} description={tooltipDescription} />
        </strong>{" "}
        {displayValue}
      </li>
    );
  };

  // ✅ หน้ารอโหลด
  if (loading) {
    return (
      <div className="loading-container">
        <h2>กำลังโหลดข้อมูล...</h2>
        <div className="spinner"></div>
      </div>
    );
  }

  // ✅ หน้าข้อผิดพลาด
  if (error) {
    return (
      <div className="error-container">
        <h2>เกิดข้อผิดพลาด</h2>
        <p>{error}</p>
        <button className="btn btn-primary" onClick={fetchPackageData}>
          ลองใหม่อีกครั้ง
        </button>
      </div>
    );
  }

// ✅ หน้าหลักแสดงรายละเอียด
// ✅ หน้าหลักแสดงรายละเอียด
return (
  <div className="package-detail">
    {/* ✅ โลโก้บริษัท + ชื่อบริษัท */}
    <div className="company-info text-center mb-4">
      {console.log("🏷️ Raw company name from packageData:", packageData?.company_full_name || packageData?.insurance_company)}
      <img
        src={logoUrl}
        alt={`${getFullCompanyName(packageData?.company_full_name || packageData?.insurance_company, "en")} Logo`}
        className="company-logo mb-2"
        onError={(e) => {
          console.error("❌ Error loading logo, falling back to default logo.");
          e.target.onerror = null;
          e.target.src = sanitizeLogoUrl(null);
        }}
      />
      <h2 className="company-name text-primary fw-bold">
        {getFullCompanyName(packageData?.company_full_name || packageData?.insurance_company, "th") || "ไม่ระบุบริษัท"}
      </h2>
    </div>

    {/* ✅ โลโก้และแบรนด์รถ */}
    <div className="car-brand-info">
      <img
        src={getCarLogoUrl(packageData?.car_brand)}
        alt={`${packageData?.car_brand || "ไม่ระบุ"} Logo`}
        className="car-logo"
        onLoad={() => {
          console.log(`✅ Loaded car logo: ${packageData?.car_brand}`);
        }}
        onError={(e) => {
          console.error(`❌ Car logo not found for brand: ${packageData?.car_brand}`);
          e.target.src = "/assets/car-logos/logos/thumb/default-logo.png";
        }}
      />
      <p>
        <strong>แบรนด์รถยนต์:</strong> {packageData?.car_brand || "ไม่ระบุ"}
      </p>
    </div>

  
    <div className="summary-card">
      <div className="summary-row">
        <span>💵 เบี้ยประกัน</span>
        <span>{packageData?.premium?.toLocaleString() || "ไม่ระบุ"} บาท</span>
      </div>
      <div className="summary-row">
        <span>🚗 รุ่นย่อย</span>
        <span>{packageData?.car_submodel || "ไม่ระบุ"}</span>
      </div>
      <div className="summary-row">
        <span>🛠 ประเภทการซ่อม</span>
        <span>{packageData?.repair_type || "ไม่ระบุ"}</span>
      </div>
      <div className="summary-row">
        <span>📦 แพคเกจ</span>
        <span>{packageData?.package_id || "ไม่ระบุ"}</span>
      </div>
    </div>

    
    <div className="details">
      <h3 className="coverage-title">🛡️ รายละเอียดความคุ้มครอง</h3>
      <ul className="coverage-list">
        {[
          {
            label: "ประเภทประกันภัย",
            value: packageData?.insurance_type,
            tooltipTitle: "ประเภทประกันภัย",
            tooltipDesc: "ประเภทของการประกันภัย เช่น ชั้น 1, ชั้น 2+ เป็นต้น",
          },
          {
            label: "คุ้มครองตัวรถ",
            value: packageData?.own_damage,
            tooltipTitle: "คุ้มครองตัวรถ",
            tooltipDesc: "คุ้มครองค่าซ่อมรถคุณจากอุบัติเหตุหรือความเสียหายอื่น ๆ",
          },
          {
            label: "คุ้มครองไฟไหม้/รถหาย",
            value: packageData?.own_theft_fire_damage,
            tooltipTitle: "ไฟไหม้ / รถหาย",
            tooltipDesc: "ครอบคลุมความเสียหายกรณีไฟไหม้หรือรถหาย",
          },
          {
            label: "ค่ารักษาพยาบาล",
            value: packageData?.coverage_medical_expense,
            tooltipTitle: "ค่ารักษาพยาบาล",
            tooltipDesc: "ครอบคลุมค่ารักษาพยาบาลของผู้ขับขี่และผู้โดยสาร",
          },
          {
            label: "คุ้มครองทรัพย์สิน",
            value: packageData?.liability_property,
            tooltipTitle: "ทรัพย์สินบุคคลภายนอก",
            tooltipDesc: "ชดเชยความเสียหายที่เกิดขึ้นกับทรัพย์สินของบุคคลอื่น",
          },
          {
            label: "คุ้มครองต่อคน",
            value: packageData?.liability_per_person,
            tooltipTitle: "คุ้มครองต่อคน",
            tooltipDesc: "วงเงินสูงสุดต่อคน สำหรับความเสียหายต่อร่างกายหรือชีวิต",
          },
          {
            label: "คุ้มครองต่อเหตุการณ์",
            value: packageData?.liability_per_event,
            tooltipTitle: "คุ้มครองต่อเหตุการณ์",
            tooltipDesc: "วงเงินสูงสุดรวมทั้งหมดต่ออุบัติเหตุ 1 ครั้ง",
          },
          {
            label: "ประกันตัวผู้ขับขี่",
            value: packageData?.coverage_bail_bond,
            tooltipTitle: "ประกันตัวผู้ขับขี่",
            tooltipDesc: "ค่าประกันตัวกรณีผู้ขับมีคดีอาญาเกิดจากอุบัติเหตุ",
          },
        ].map(({ label, value, tooltipTitle, tooltipDesc }, index) =>
          renderCoverageDetail(label, value, tooltipTitle, tooltipDesc)
        )}
      </ul>
    </div>




      
      {/* เพิ่ม CoverageDateTime Component */}
      <div className="coverage-date-time-section">
        <h3>🗓️ เลือกวันที่และเวลาคุ้มครอง</h3>
        <CoverageDateTime onSave={handleCoverageDateTimeSave} />
        {coverageDateTime.date && (
          <p className="coverage-date-summary">
            <strong>วันที่ที่เลือก:</strong> {coverageDateTime.date} <br />
            <strong>เวลา:</strong> {coverageDateTime.time}
          </p>
        )}
      </div>

      {/* ส่วนสำหรับใช้คูปอง */}
      <div className="coupon-section">
        <h3>🎟️ ใช้คูปองส่วนลด</h3>
        <input
          type="text"
          className="coupon-input"
          placeholder="กรอกโค้ดคูปอง"
          onBlur={(e) => {
            const couponCode = e.target.value.trim();
            const coupon = coupons.find((c) => c.code === couponCode);
            if (coupon) {
              setAppliedCoupon(coupon);
              alert(`ใช้คูปองสำเร็จ: ลด ${coupon.discount} บาท`);
            } else {
              alert("ไม่พบคูปองนี้");
              setAppliedCoupon(null);
            }
          }}
        />
        {appliedCoupon && (
          <p className="applied-coupon">
            <strong>คูปองที่ใช้:</strong> {appliedCoupon.code} <br />
            <strong>ส่วนลด:</strong> {appliedCoupon.discount.toLocaleString()} บาท
          </p>
        )}
      </div>

      {/* ส่วนปรับตัวเลือก */}
      <div className="cmi-adjustment">
        <h3>🔧 เลือกตัวเลือกเพิ่มเติม</h3>
        <label className="cmi-option">
          <input
            type="checkbox"
            checked={includeCmi}
            onChange={() => setIncludeCmi((prev) => !prev)}
          />
          รวมค่า พรบ. ({packageData?.coverage?.cmi_amount?.toLocaleString() || "0"} บาท)
        </label>
      </div>

      {/* แสดงราคาสุทธิรวม */}
      {totalPrice !== null && (
        <div className="total-price">
          {/* หัวข้อใช้ gradient */}
          <h3 className="gradient-text" style={{ fontSize: "1.6rem", marginBottom: "1rem" }}>
            💰 สรุปการคำนวณ
          </h3>

          <ul className="price-breakdown">
            <li>เบี้ยประกัน: {calculation.premium.toLocaleString()} บาท</li>
            <li>อากรแสตมป์: {calculation.duty.toLocaleString()} บาท</li>
            <li>รวมก่อน VAT: {calculation.totalBeforeVat.toLocaleString()} บาท</li>
            <li>VAT (7%): {calculation.vat.toLocaleString()} บาท</li>

            {includeCmi && (
              <li>ค่า พรบ.: {packageData.coverage?.cmi_amount?.toLocaleString()} บาท</li>
            )}

            {selectedAddOns.length > 0 && (
              <li>
                <strong>แพ็กเกจเสริมที่เลือก:</strong>
                <ul>
                  {partnerAddOns
                    .filter((addOn) => selectedAddOns.includes(addOn.id))
                    .map((addOn) => (
                      <li key={addOn.id}>
                        {addOn.name} ({addOn.price.toLocaleString()} บาท)
                      </li>
                    ))}
                </ul>
              </li>
            )}

            {/* ✅ ไม่ใช้ gradient แต่ใช้สีส้มแบรนด์แทน */}
            <li>
              <strong style={{ fontSize: "1.3rem", color: "#E67E22" }}>
                ราคาสุทธิรวม: {totalPrice.toLocaleString()} บาท
              </strong>
            </li>
          </ul>
        </div>
      )}




      {/* ปุ่มดำเนินการ */}
      <div className="actions">
        <button
          className="btn btn-success"
          onClick={handlePurchase}
          disabled={loadingPurchase || !coverageDateTime?.date}
        >
          {loadingPurchase ? "กำลังดำเนินการ..." : "ซื้อเลย"}
        </button>

        <button
          className="btn btn-secondary"
          onClick={() => navigate(-1)}
        >
          ย้อนกลับ
        </button>
      </div>

      {/* แสดงข้อความ error ถ้ามี */}
      {error && (
        <div className="error-message">
          <strong>เกิดข้อผิดพลาด:</strong> {error || "ไม่สามารถดำเนินการได้"}
        </div>
      )}




    </div>
  );
  
  
};

export default PackageDetail;
