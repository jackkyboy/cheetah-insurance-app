# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/mandatoryInsuranceMapping.py
import logging

# ตั้งค่า Logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def getInsuranceDetails(vehicle_type, usage_type, engine_size=None, seating_capacity=None, weight=None):
    """
    ดึงข้อมูลประกันภัยภาคบังคับตามประเภทของรถและขนาด

    Parameters:
    - vehicle_type (str): ประเภทของรถ เช่น "motorcycles", "passenger_cars", "trucks"
    - usage_type (str): ประเภทการใช้งาน เช่น "personal", "commercial"
    - engine_size (int, optional): ขนาดเครื่องยนต์ (cc) สำหรับจักรยานยนต์
    - seating_capacity (int, optional): จำนวนที่นั่ง สำหรับรถโดยสาร
    - weight (int, optional): น้ำหนัก (ตัน) สำหรับรถบรรทุก

    Returns:
    dict: รายละเอียดประกันภัย หรือข้อความแสดงข้อผิดพลาด
    """
    logger.debug(f"🔍 [getInsuranceDetails] Input: vehicle_type={vehicle_type}, "
                 f"usage_type={usage_type}, engine_size={engine_size}, seating_capacity={seating_capacity}, weight={weight}")

    # 🔍 Mapping ตารางราคา
    insurance_mapping = {
        "motorcycles": {
            "personal": {
                "75cc_below": {"total": 161.57, "code": "1.30A"},
                "75cc_to_125cc": {"total": 323.14, "code": "1.30B"},
                "125cc_to_150cc": {"total": 430.14, "code": "1.30C"},
                "above_150cc": {"total": 645.21, "code": "1.30D"},
            }
        },
        "passenger_cars": {
            "personal": {
                "7_seats_below": {"total": 645.21, "code": "1.10A"},
                "15_seats_below": {"total": 1182.35, "code": "1.20A"},
                "15_to_20_seats": {"total": 2203.13, "code": "1.20B"},
                "20_to_40_seats": {"total": 3437.91, "code": "1.20C"},
                "above_40_seats": {"total": 4017.85, "code": "1.20D"},
            }
        },
        "trucks": {
            "personal": {
                "up_to_3_tons": {"total": 967.28, "code": "1.40A"},
                "3_to_6_tons": {"total": 1310.75, "code": "1.40B"},
                "6_to_12_tons": {"total": 1408.12, "code": "1.40C"},
                "above_12_tons": {"total": 1826.49, "code": "1.40D"},
            }
        },
        "electric_vehicles": {
            "personal": {
                "motorcycles": {"total": 323.14, "code": "EV1"},
                "passenger_cars": {"total": 2041.56, "code": "EV2"},
            }
        },
        "trailers": {
            "personal": {"default": {"total": 645.21, "code": "TR1"}},
        },
        "red_plate_cars": {
            "personal": {"default": {"total": 1644.59, "code": "RP1"}},
        },
        "agricultural_vehicles": {
            "personal": {"default": {"total": 97.37, "code": "AG1"}},
        }
    }

    # ✅ ตรวจสอบว่า `vehicle_type` มีในระบบหรือไม่
    vehicle_data = insurance_mapping.get(vehicle_type)
    if not vehicle_data:
        logger.error(f"❌ ไม่พบข้อมูลสำหรับประเภทของรถ '{vehicle_type}'")
        return {"error": f"ไม่พบข้อมูลสำหรับประเภทของรถ '{vehicle_type}'"}

    # ✅ ตรวจสอบประเภทการใช้งาน
    usage_data = vehicle_data.get(usage_type)
    if not usage_data:
        logger.error(f"❌ ไม่พบข้อมูลสำหรับประเภทการใช้งาน '{usage_type}'")
        return {"error": f"ไม่พบข้อมูลสำหรับประเภทการใช้งาน '{usage_type}'"}

    # 🛵 เงื่อนไขสำหรับจักรยานยนต์
    if vehicle_type == "motorcycles":
        if engine_size is None:
            logger.warning(f"⚠️ กรุณาระบุขนาดเครื่องยนต์ (cc)")
            return {"error": "กรุณาระบุขนาดเครื่องยนต์ (cc)"}
        if engine_size <= 75:
            return usage_data["75cc_below"]
        elif engine_size <= 125:
            return usage_data["75cc_to_125cc"]
        elif engine_size <= 150:
            return usage_data["125cc_to_150cc"]
        else:
            return usage_data["above_150cc"]

    # 🚗 เงื่อนไขสำหรับรถโดยสาร
    if vehicle_type == "passenger_cars":
        if seating_capacity is None:
            seating_capacity = 5  # ✅ ใช้ค่าเริ่มต้นเป็น 5 ที่นั่ง
            logger.warning(f"⚠️ [getInsuranceDetails] ใช้ค่าเริ่มต้น Seating Capacity: 5")
        if seating_capacity <= 7:
            return usage_data["7_seats_below"]
        elif seating_capacity <= 15:
            return usage_data["15_seats_below"]
        elif seating_capacity <= 20:
            return usage_data["15_to_20_seats"]
        elif seating_capacity <= 40:
            return usage_data["20_to_40_seats"]
        else:
            return usage_data["above_40_seats"]

    # 🚚 เงื่อนไขสำหรับรถบรรทุก
    if vehicle_type == "trucks":
        if weight is None:
            logger.warning(f"⚠️ กรุณาระบุน้ำหนัก (ตัน)")
            return {"error": "กรุณาระบุน้ำหนัก (ตัน)"}
        if weight <= 3:
            return usage_data["up_to_3_tons"]
        elif weight <= 6:
            return usage_data["3_to_6_tons"]
        elif weight <= 12:
            return usage_data["6_to_12_tons"]
        else:
            return usage_data["above_12_tons"]

    # 🚜 รถที่ขับเคลื่อนด้วยพลังงานไฟฟ้า / รถพ่วง / รถป้ายแดง / รถเกษตร
    if vehicle_type in ["electric_vehicles", "trailers", "red_plate_cars", "agricultural_vehicles"]:
        return usage_data["default"]

    logger.error(f"❌ ไม่พบข้อมูลประกันสำหรับ '{vehicle_type}'")
    return {"error": f"ไม่พบข้อมูลสำหรับ '{vehicle_type}'"}




# 🚀 ทดสอบโค้ด
if __name__ == "__main__":
    print(getInsuranceDetails("motorcycles", "personal", engine_size=125))
    print(getInsuranceDetails("passenger_cars", "personal", seating_capacity=7))
    print(getInsuranceDetails("trucks", "personal", weight=5))
    print(getInsuranceDetails("electric_vehicles", "personal"))
    print(getInsuranceDetails("trailers", "personal"))
    print(getInsuranceDetails("red_plate_cars", "personal"))
    print(getInsuranceDetails("agricultural_vehicles", "personal"))