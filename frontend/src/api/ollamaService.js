const API_BASE = process.env.REACT_APP_API_BASE || "http://127.0.0.1:5000";

// 🔸 บริษัทที่อนุญาตให้ตอบกลับ
const allowedCompanies = [
  "ชับบ์", "ERGO", "เมืองไทยประกันภัย", "วิริยะ",
  "AXA", "ทิพยประกันภัย", "กรุงไทยพานิช", "MSIG", "โตเกียวมารีน",
];

// 🧠 ส่ง Prompt ไปยัง Ollama พร้อมกฎห้ามแบบเข้มงวด
export async function askOllama(prompt) {
  const companyNote = `
[ระบบเข้มงวด]
กรุณาตอบเฉพาะบริษัทประกันภัยต่อไปนี้เท่านั้น: ${allowedCompanies.join(", ")}  
ห้ามแปลชื่อ ห้ามแต่งชื่อบริษัทอื่นเพิ่มเติม  
ห้ามเดาตัวเลขเบี้ย ห้ามตอบช่วงเบี้ย ห้ามลิสต์รายชื่อบริษัททั้งหมด  
ห้ามมีข้อความใด ๆ เกินกว่า 1 บรรทัด  
ถ้าไม่มีข้อมูลจากบริษัทเหล่านี้ ให้ตอบว่า: ไม่มีข้อมูลในระบบ
ห้ามพิมพ์เครื่องหมายดอกจัน (*), ตัวเลขนำหน้า, หรืออักษรพิเศษใด ๆ
`.trim();

  const fullPrompt = `${prompt.trim()}\n${companyNote}`;

  try {
    const res = await fetch(`${API_BASE}/api/ollama/ask-ollama`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: fullPrompt }),
    });

    if (!res.ok) throw new Error("Ollama API call failed");

    const data = await res.json();
    const rawReply = data?.response || "";
    const cleanReply = sanitizeOllamaReply(rawReply);
    console.log("🧠 Ollama raw:", rawReply);
    console.log("✅ Cleaned reply:", cleanReply);

    return cleanReply;
  } catch (err) {
    console.error("🔥 Ollama Error:", err);
    return "⚠️ เกิดข้อผิดพลาดในการเชื่อมต่อกับเซิร์ฟเวอร์";
  }
}

// 🔍 ตรวจจับเบี้ยปลอม เช่น 143,111 หรือ 35,000 - 45,000
export function detectFabricatedPremium(text) {
  const suspiciousComma = /\d{2,3},\d{3}/g;
  const rangePattern = /฿?\d{2,3},\d{3}\s*-\s*฿?\d{2,3},\d{3}/g;
  return suspiciousComma.test(text) || rangePattern.test(text) || /[0-9]{4,5}\s*บาท/.test(text);
}

// 🧼 ปรับข้อความตอบกลับให้เหลือเฉพาะสิ่งที่เชื่อถือได้
export function sanitizeOllamaReply(text) {
  if (!text) return "ไม่มีข้อมูลในระบบ";

  const clean = text.trim();
  const hasMultipleLines = clean.split("\n").length > 1;
  const hasCommaList = clean.includes(",") && allowedCompanies.some(name => clean.includes(name));
  const hasBullet = clean.includes("*") || /^\d+\./.test(clean);
  const hasFakePrice = detectFabricatedPremium(clean);
  const hasMultipleCompanies = allowedCompanies.filter(name => clean.includes(name)).length > 1;

  if (
    hasMultipleLines ||
    hasCommaList ||
    hasBullet ||
    hasFakePrice ||
    hasMultipleCompanies
  ) {
    console.warn("⚠️ Ollama ตอบผิดกฎ — ปรับเป็น 'ไม่มีข้อมูลในระบบ'");
    return "ไม่มีข้อมูลในระบบ";
  }

  return clean;
}

// 🧾 แปลงข้อความจาก Ollama เป็นรายการแพ็กเกจ
export function parseOllamaToPackages(rawText, defaultType = "3+") {
  const companyMapping = {
    "ชับบ์": "chubb",
    "ERGO": "ergo",
    "เมืองไทยประกันภัย": "mti",
    "วิริยะ": "viriyah",
    "AXA": "axa",
    "ทิพยประกันภัย": "dhip",
    "กรุงไทยพานิช": "kpi",
    "MSIG": "msig",
    "โตเกียวมารีน": "tki",
  };

  const allowedCompanyNames = Object.keys(companyMapping);
  const lines = rawText.split("\n").filter((line) => line.trim());
  const results = [];

  for (const line of lines) {
    const match =
      line.match(/^(\d+)\.\s*([^\d:：]+?):?\s*(.+)$/) ||
      line.match(/^([^\d:：]+?):?\s*(.+)$/);

    if (!match) continue;

    const [, rawCompany, rawDesc] = match.length === 4 ? match.slice(1) : ["", ...match.slice(1)];
    const companyName = rawCompany.trim();
    const descriptionRaw = rawDesc?.trim() || "";

    // ❌ ข้ามบริษัทนอก whitelist
    if (!allowedCompanyNames.includes(companyName)) {
      console.warn("❌ บริษัทไม่อยู่ในลิสต์:", companyName);
      continue;
    }

    const code = companyMapping[companyName];
    if (!code || descriptionRaw.includes("ไม่มีข้อมูล")) continue;

    const isFabricated = detectFabricatedPremium(descriptionRaw);
    if (isFabricated) {
      console.warn("⚠️ ข้ามเบี้ยแต่งเอง:", descriptionRaw);
      continue;
    }

    results.push({
      insurance_company: companyName,
      code,
      insurance_type: defaultType,
      net_premium_range: "ไม่ระบุ",
      description: descriptionRaw,
      flagged_fake_price: false,
    });
  }

  return results;
}

