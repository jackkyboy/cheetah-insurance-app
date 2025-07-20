/*/Users/apichet/Downloads/cheetah-insurance-app/src/api/paymentService.js */
import axios from "./axios";
import jwtDecode from "jwt-decode";

// 🔍 ตรวจสอบว่ามีฟิลด์จำเป็นครบ
const validatePayload = (payload, requiredFields) => {
  const missing = requiredFields.filter(
    (field) => !payload[field] || payload[field] === ""
  );
  if (missing.length > 0) {
    throw new Error(`Missing required fields: ${missing.join(", ")}`);
  }
};

// 🔐 Decode JWT อย่างปลอดภัย
const decodeJwtPayload = (token) => {
  try {
    const decoded = jwtDecode(token);
    console.debug("🧠 Decoded JWT:", decoded);
    return decoded;
  } catch (err) {
    console.error("❌ Failed to decode JWT:", err);
    throw new Error("JWT format ไม่ถูกต้อง");
  }
};

// 🚀 สร้างคำสั่งชำระเงินและ redirect ไปยัง 2C2P
// 🚀 สร้างคำสั่งชำระเงินและ redirect ไปยัง 2C2P
export const createPaymentOrder = async (payload) => {
  try {
    validatePayload(payload, ["customer_id", "amount", "currency"]);

    const res = await axios.post("/payments/create", payload);
    const raw = res?.data;
    console.debug("📦 Raw backend response:", raw);

    const jwtString = raw?.payload;

    if (typeof jwtString !== "string") {
      console.error("⚠️ payload is not a string:", jwtString);
      throw new Error("ข้อมูลการชำระเงินไม่สมบูรณ์");
    }

    // ✅ เช็กว่าเป็น JWT แบบ 3 ส่วน
    const parts = jwtString.split(".");
    if (parts.length !== 3) {
      console.error("⚠️ JWT format is invalid:", jwtString);
      throw new Error("ข้อมูลการชำระเงินไม่สมบูรณ์");
    }

    const decoded = decodeJwtPayload(jwtString);

    // ✅ ลองทุก field ที่เป็นไปได้
    const redirectUrl = decoded?.webPaymentUrl || decoded?.web_payment_url || decoded?.paymentUrl || decoded?.url;

    if (!redirectUrl || typeof redirectUrl !== "string" || !redirectUrl.startsWith("http")) {
      console.error("❌ URL สำหรับ redirect ไม่พบใน JWT:", decoded);
      throw new Error("ไม่พบ URL สำหรับชำระเงินใน JWT ที่ส่งมา");
    }

    console.info("🔗 Redirecting user to:", redirectUrl);
    window.location.href = redirectUrl;

    return raw;
  } catch (error) {
    const errMsg = error?.response?.data?.error || error.message || "ไม่สามารถสร้างคำสั่งชำระเงินได้";
    console.error("❌ [createPaymentOrder]", errMsg);
    throw new Error(errMsg);
  }
};



// 📦 ดึงช่องทางชำระเงินที่รองรับ
export const fetchPaymentOptions = async (paymentToken) => {
  try {
    if (!paymentToken) throw new Error("Payment token is required.");
    const res = await axios.post("/payments/options", { payment_token: paymentToken });
    return res.data;
  } catch (error) {
    const errMsg = error?.response?.data?.error || error.message;
    console.error("❌ [fetchPaymentOptions]", errMsg);
    throw new Error(errMsg);
  }
};

// 📄 ตรวจสอบสถานะการชำระเงิน
export const getPaymentStatus = async (orderId) => {
  try {
    if (!orderId) throw new Error("Order ID is required.");
    const res = await axios.get(`/payments/status/${orderId}`);
    return res.data;
  } catch (error) {
    const errMsg = error?.response?.data?.error || error.message;
    console.error("❌ [getPaymentStatus]", errMsg);
    throw new Error(errMsg);
  }
};

// 🔗 สร้าง URL ชำระเงินแบบ manual
export const generatePaymentUrl = async (payload) => {
  try {
    validatePayload(payload, ["amount", "order_id"]);
    const res = await axios.post("/payments/generate-url", payload);
    const url = res?.data?.paymentUrl;
    if (!url) throw new Error("ไม่พบ Payment URL ใน response.");
    return url;
  } catch (error) {
    const errMsg = error?.response?.data?.error || error.message;
    console.error("❌ [generatePaymentUrl]", errMsg);
    throw new Error(errMsg);
  }
};
