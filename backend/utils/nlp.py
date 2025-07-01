

# ✅ /Users/apichet/Downloads/cheetah-insurance-app/backend/utils/nlp.py
# ✅ /Users/apichet/Downloads/cheetah-insurance-app/backend/utils/nlp.py
import re
from collections import namedtuple

ParsedQuery = namedtuple("ParsedQuery", ["brand", "model", "year", "insurance_type"])

def parseInsuranceQuery(prompt: str) -> ParsedQuery:
    prompt = prompt.strip()

    # 🔍 Brand
    brand_match = re.search(
        r"\b(toyota|honda|nissan|isuzu|mazda|bmw|benz|mercedes|merc|mb|mitsubishi|audi|lexus)\b",
        prompt, re.IGNORECASE
    )

    # 🔍 Model
    model_match = re.search(
        r"\b(camry|civic|jazz|dmax|cx-5|series 3|mirage|altis|a4|a6|c-class|e-class)\b",
        prompt, re.IGNORECASE
    )

    # 🔍 Year
    year_match = re.search(r"\b(20\d{2})\b", prompt)

    # 🔍 Type
    type_patterns = [
        r"(?:ประกัน)?\s*(?:ชั้น|ประเภท)?\s*([123][\+pP]?)",
        r"(?:ประกัน)?\s*(?:ชั้น|ประเภท)?\s*(0)",
        r"(ชั้น\s?2\s?พลัส|2\s?plus)",
    ]
    insurance_type = None
    for pattern in type_patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            insurance_type = match.group(1).lower()
            break

    if insurance_type:
        insurance_type = (
            insurance_type
            .replace("p", "+")
            .replace("พลัส", "+")
            .replace("plus", "+")
            .replace(" ", "")
        )

    brand = brand_match.group(1).lower() if brand_match else None
    if brand:
        brand = brand.replace("benz", "mercedes-benz").replace("mercedes", "mercedes-benz").replace("merc", "mercedes-benz").replace("mb", "mercedes-benz")

    model = model_match.group(1).lower() if model_match else None
    year = year_match.group(1) if year_match else None

    return ParsedQuery(brand, model, year, insurance_type)
