# /Users/apichet/Downloads/cheetah-insurance-app/backend/services/ollama_service.py
import requests
import logging
import re

OLLAMA_API_URL = "http://127.0.0.1:5000/api/ollama/ask-ollama"

ALLOWED_COMPANIES = [
    "ชับบ์",
    "ERGO",
    "เมืองไทยประกันภัย",
    "วิริยะ",
    "AXA",
    "ทิพยประกันภัย",
    "กรุงไทยพานิช",
    "MSIG",
    "โตเกียวมารีน",
]

def askOllamaWithData(prompt: str) -> str:
    try:
        strict_instruction = (
            "[ระบบเข้มงวด]\n\n"
            "ขอข้อมูลประกันภัยชั้น 1 สำหรับ Honda Civic ปี 2022\n\n"
            f"กรุณาตอบเฉพาะบริษัทประกันภัยต่อไปนี้เท่านั้น: {', '.join(ALLOWED_COMPANIES)}\n"
            "ห้ามแปลชื่อ ห้ามแต่งชื่อบริษัทอื่นเพิ่มเติม\n"
            "ห้ามเดาตัวเลขเบี้ย ห้ามตอบช่วงเบี้ย\n"
            "ห้ามลิสต์รายชื่อบริษัททั้งหมดแม้ในรูปแบบคอมม่า (,)\n"
            "ห้ามมีข้อความใด ๆ เกินกว่า 1 บรรทัด\n"
            "ห้ามพิมพ์เครื่องหมายดอกจัน (*), ตัวเลขนำหน้า, หรืออักษรพิเศษใด ๆ\n\n"
            'ถ้าไม่มีข้อมูลจากบริษัทเหล่านี้ ให้ตอบว่า: ไม่มีข้อมูลในระบบ\n'
            "ห้ามตอบอย่างอื่นโดยเด็ดขาด"
        )

        full_prompt = f"{prompt.strip()}\n{strict_instruction}"

        response = requests.post(
            OLLAMA_API_URL,
            json={"prompt": full_prompt},
            headers={"Content-Type": "application/json"},
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        raw_reply = data.get("response", "").strip()
        reply = sanitizeOllamaReply(raw_reply)
        return reply or "❌ ไม่สามารถตอบกลับได้"

    except requests.exceptions.RequestException as err:
        logging.error(f"Ollama API request failed: {err}")
        return "⚠️ เกิดข้อผิดพลาดในการเชื่อมต่อกับเซิร์ฟเวอร์"


def sanitizeOllamaReply(text: str) -> str:
    """
    ตรวจสอบคำตอบที่ได้จาก Ollama ว่าผ่านเงื่อนไขหรือไม่
    หากไม่ผ่าน ให้ return 'ไม่มีข้อมูลในระบบ'
    """
    if not text:
        return "ไม่มีข้อมูลในระบบ"

    lines = text.strip().split("\n")
    contains_asterisk = "*" in text
    starts_with_number = bool(re.match(r"^\d+\.", text.strip()))
    has_comma = "," in text
    has_multiple_lines = len(lines) > 1
    multiple_companies = sum(company in text for company in ALLOWED_COMPANIES) > 1
    has_fake_price = contains_fabricated_price(text)

    if (
        has_multiple_lines or
        contains_asterisk or
        starts_with_number or
        has_comma or
        multiple_companies or
        has_fake_price
    ):
        logging.warning("⚠️ ตอบกลับผิดกฎ: ปรับให้เป็น 'ไม่มีข้อมูลในระบบ'")
        return "ไม่มีข้อมูลในระบบ"

    return text.strip()



def contains_fabricated_price(text: str) -> bool:
    return bool(re.search(r"\d{1,3},\d{3}", text) or re.search(r"\b\d{4,5}\b", text))


def is_valid_premium(low: int, high: int) -> bool:
    return 1000 <= low <= high <= 50000

# (parseOllamaToPackages remains the same unless you want to block responses here too)


def parseOllamaToPackages(rawText: str, defaultType="3+") -> list:
    import re

    companyMapping = {
        "ชับบ์": "chubb",
        "ERGO": "ergo",
        "เมืองไทยประกันภัย": "mti",
        "วิริยะ": "viriyah",
        "AXA": "axa",
        "ทิพยประกันภัย": "dhip",
        "กรุงไทยพานิช": "kpi",
        "MSIG": "msig",
        "โตเกียวมารีน": "tki",
    }

    allowedCompanyNames = set(companyMapping.keys())
    results = []

    lines = [line.strip() for line in rawText.split("\n") if line.strip()]
    currentCompany = None

    for line in lines:
        line = re.sub(r"\(.*?\)", "", line).strip()

        # 🧱 บริษัทหลัก
        main_match = re.match(r"^\*?\s*(?:\d+\.\s*)?([^\d:：\*]+?):\s*(.+)?$", line)
        if main_match:
            companyName = main_match.group(1).strip()
            descriptionRaw = main_match.group(2).strip() if main_match.group(2) else ""

            if companyName not in allowedCompanyNames or "ไม่มีข้อมูล" in descriptionRaw:
                currentCompany = None
                continue

            currentCompany = companyName
            if descriptionRaw:
                description = re.sub(r"[.。]?$", "", descriptionRaw).strip()
                description = re.sub(r"ขึ้นอยู่กับ.*$", "", description, flags=re.IGNORECASE)
                description = re.sub(r"^ประมาณ", "", description, flags=re.IGNORECASE)

                premiumMatch = re.search(r"(\d{1,3}(?:,\d{3})*)\s*-\s*(\d{1,3}(?:,\d{3})*)", description)
                if not premiumMatch:
                    continue

                low = int(premiumMatch.group(1).replace(",", ""))
                high = int(premiumMatch.group(2).replace(",", ""))
                if not is_valid_premium(low, high):
                    continue

                results.append({
                    "insurance_company": companyName,
                    "code": companyMapping[companyName],
                    "insurance_type": defaultType,
                    "net_premium_range": f"{premiumMatch.group(1)} - {premiumMatch.group(2)}",
                    "description": description,
                })
            continue

        # 🔽 แพ็กเกจย่อยแบบ - Package: price
        if currentCompany:
            sub_match = re.match(r"^-+\s*([^:]+):\s*(.+)$", line)
            if not sub_match:
                continue

            packageName = sub_match.group(1).strip()
            description = sub_match.group(2).strip()
            description = re.sub(r"[.。]?$", "", description).strip()
            description = re.sub(r"ขึ้นอยู่กับ.*$", "", description, flags=re.IGNORECASE)
            description = re.sub(r"^ประมาณ", "", description, flags=re.IGNORECASE)

            premiumMatch = re.search(r"(\d{1,3}(?:,\d{3})*)\s*-\s*(\d{1,3}(?:,\d{3})*)", description)
            if not premiumMatch:
                continue

            low = int(premiumMatch.group(1).replace(",", ""))
            high = int(premiumMatch.group(2).replace(",", ""))
            if not is_valid_premium(low, high):
                continue

            results.append({
                "insurance_company": currentCompany,
                "code": companyMapping[currentCompany],
                "insurance_type": defaultType,
                "net_premium_range": f"{premiumMatch.group(1)} - {premiumMatch.group(2)}",
                "description": f"{packageName} - {description}",
            })

    # ✅ Flag ว่าอาจแต่ง (ไม่มี net_premium หรือ package_code ที่มาจาก BQ)
    for r in results:
        if "net_premium" not in r and "package_code" not in r:
            r["flagged_fake_price"] = True

    return results


