/*/Users/apichet/Downloads/cheetah-insurance-app/src/api/mandatoryInsuranceMapping.js */
// JSON Data - Insurance Rates
// JSON Data - Insurance Rates
const mandatoryInsuranceMapping = {
    motorcycles: {
        below_75cc: { personal: 300, commercial: 350 },
        "75cc_to_125cc": { personal: 400, commercial: 450 },
        "125cc_to_150cc": { personal: 500, commercial: 550 },
        above_150cc: { personal: 600, commercial: 650 },
    },
    electricVehicles: {
        personal_ev: { personal: 1900, commercial: 2500 },
        commercial_ev: { personal: 2500, commercial: 3500 },
    },
    passengerCars: {
        up_to_7_seats_bkk: { personal: 600, commercial: 1900 },
        up_to_7_seats_upcountry: { personal: 1200, commercial: 2500 },
        above_7_seats_up_to_15: { personal: 1100, commercial: 2320 },
        above_15_seats: { personal: 2050, commercial: 3480 },
    },
    trucks: {
        up_to_3_tons: { personal: 900, commercial: 1760 },
        "3_to_6_tons": { personal: 1400, commercial: 2300 },
        "6_to_12_tons": { personal: 1310, commercial: 2000 },
        above_12_tons: { personal: 1600, commercial: 2700 },
    },
    trailers: {
        general_trailer: { personal: 2000, commercial: 3200 },
    },
};

// ✅ Function to determine vehicle type
// ✅ ปรับโครงสร้าง determineVehicleType ให้แม่นยำขึ้น
// ✅ ปรับ determineVehicleType ให้ตรวจสอบค่าที่ถูกต้อง
// ✅ ฟังก์ชันตรวจสอบข้อมูลก่อนใช้งาน
export const validateInputData = (seatingCapacity, engineCC, weight, usage, area, isElectric) => {
    console.log(
        "🔍 [validateInputData] Raw Input:",
        "| Seating Capacity:", seatingCapacity,
        "| Engine CC:", engineCC,
        "| Weight:", weight,
        "| Usage:", usage,
        "| Area:", area,
        "| Electric:", isElectric
    );

    // 🚨 ตรวจสอบค่าที่อาจผิดพลาด
    if (isNaN(seatingCapacity) || seatingCapacity <= 0) {
        console.warn("⚠️ Seating Capacity ไม่ใช่ตัวเลข:", seatingCapacity);
        seatingCapacity = null;
    }

    if (isNaN(engineCC) || engineCC <= 0) {
        console.warn("⚠️ Engine CC ไม่ใช่ตัวเลข:", engineCC);
        engineCC = null;
    }

    if (isNaN(weight) || weight <= 0 || weight >= 50) {
        if (weight >= 1900) {
            console.warn("⚠️ Weight อาจเป็น Model Year (ปีรถ) แทน:", weight);
        } else {
            console.warn("⚠️ Weight ไม่ใช่ค่าที่ถูกต้อง:", weight);
        }
        weight = null;
    }

    if (!usage) {
        console.warn("⚠️ Usage ไม่ถูกกำหนด ใช้ค่าเริ่มต้นเป็น 'ส่วนบุคคล'");
        usage = "ส่วนบุคคล";
    }

    if (!area) {
        console.warn("⚠️ Area ไม่ถูกกำหนด ใช้ค่าเริ่มต้นเป็น 'กรุงเทพฯ'");
        area = "กรุงเทพฯ";
    }

    return { seatingCapacity, engineCC, weight, usage, area, isElectric };
};

// ✅ ฟังก์ชันระบุประเภทของรถ
// ✅ ฟังก์ชันตรวจสอบและแปลงค่าข้อมูลที่ป้อนเข้า
export const normalizeInputData = (seatingCapacity, engineCC, weight, usage, area, isElectric) => {
    console.log(
        "🔍 [normalizeInputData] Raw Input:",
        "| Seating Capacity:", seatingCapacity,
        "| Engine CC:", engineCC,
        "| Weight:", weight,
        "| Usage:", usage,
        "| Area:", area,
        "| Electric:", isElectric
    );

    // ✅ ตรวจสอบว่า Seating Capacity เป็นตัวเลข
    let parsedSeatingCapacity = parseInt(seatingCapacity, 10);
    if (isNaN(parsedSeatingCapacity) || parsedSeatingCapacity <= 0) {
        console.warn("⚠️ Seating Capacity ไม่ใช่ตัวเลขหรือไม่มีค่า:", seatingCapacity);
        parsedSeatingCapacity = null;
    }

    // ✅ ตรวจสอบว่า Engine CC เป็นตัวเลข
    let parsedEngineCC = parseInt(engineCC, 10);
    if (isNaN(parsedEngineCC) || parsedEngineCC <= 0) {
        console.warn("⚠️ Engine CC ไม่ใช่ตัวเลขหรือไม่มีค่า:", engineCC);
        parsedEngineCC = null;
    }

    // ✅ ตรวจสอบว่า Weight เป็นตัวเลข และไม่ใช่ Model Year
    let parsedWeight = parseInt(weight, 10);
    let modelYear = null;
    if (!isNaN(parsedWeight)) {
        const currentYear = new Date().getFullYear();
        if (parsedWeight >= 1900 && parsedWeight <= currentYear) {
            console.warn("⚠️ Weight อาจเป็นปีรถยนต์แทน:", weight);
            modelYear = parsedWeight;
            parsedWeight = null;
        } else if (parsedWeight > 50) {
            console.warn("⚠️ Weight มากเกินไป อาจไม่ใช่ค่าน้ำหนักที่ถูกต้อง:", weight);
            parsedWeight = null;
        }
    } else {
        parsedWeight = null;
    }

    // ✅ ตั้งค่าเริ่มต้นให้ Usage และ Area
    if (!usage) {
        console.warn("⚠️ Usage ไม่ถูกกำหนด ใช้ค่าเริ่มต้นเป็น 'ส่วนบุคคล'");
        usage = "ส่วนบุคคล";
    }

    if (!area) {
        console.warn("⚠️ Area ไม่ถูกกำหนด ใช้ค่าเริ่มต้นเป็น 'กรุงเทพฯ'");
        area = "กรุงเทพฯ";
    }

    return { 
        seatingCapacity: parsedSeatingCapacity, 
        engineCC: parsedEngineCC, 
        weight: parsedWeight, 
        modelYear, 
        usage, 
        area, 
        isElectric 
    };
};





// ✅ ฟังก์ชันระบุประเภทของรถ
export const determineVehicleType = (seatingCapacity, engineCC, weight, modelYear, isElectric) => {
    console.log(
      "🔍 [determineVehicleType] Processed Input:",
      "| Seating Capacity:", seatingCapacity,
      "| Engine CC:", engineCC,
      "| Weight:", weight,
      "| Model Year:", modelYear,
      "| Electric:", isElectric
    );

    // ✅ ตรวจสอบว่ารถเป็นรถยนต์ไฟฟ้าหรือไม่
    if (isElectric) return "electricVehicles";

    // ✅ กรณีที่ไม่มีข้อมูลเพียงพอ
    if (!seatingCapacity && !engineCC && !weight) {
        console.warn("⚠️ ไม่สามารถระบุประเภทของรถจาก Model Year เพียงอย่างเดียว");
        return "unknown";
    }

    // ✅ ใช้ Engine CC เพื่อระบุประเภทของรถ
    if (engineCC !== null) {
        if (engineCC <= 150) return "motorcycles"; // รถจักรยานยนต์
        if (engineCC > 150 && engineCC <= 2000) return "passengerCars"; // รถเก๋ง
        return "trucks"; // รถบรรทุก
    }

    // ✅ ใช้ Seating Capacity เพื่อระบุประเภทของรถ
    if (seatingCapacity !== null) {
        if (seatingCapacity <= 7) return "passengerCars"; // รถเก๋ง
        if (seatingCapacity > 7 && seatingCapacity <= 15) return "minibuses"; // รถมินิบัส
        return "buses"; // รถโดยสารขนาดใหญ่
    }

    // ✅ ใช้ Weight เพื่อระบุประเภทของรถ
    if (weight !== null) {
        if (weight <= 3) return "lightTrucks"; // รถบรรทุกเล็ก
        if (weight > 3 && weight <= 12) return "mediumTrucks"; // รถบรรทุกขนาดกลาง
        return "heavyTrucks"; // รถบรรทุกขนาดใหญ่
    }

    console.warn("⚠️ ไม่สามารถระบุประเภทของรถได้");
    return "unknown";
};



// ✅ ฟังก์ชันหลักสำหรับดึงรายละเอียดประกันภัย
export const getInsuranceDetails = (seatingCapacity, engineCC, weight, usage, area, isElectric) => {
    console.log(
      "🔍 [getInsuranceDetails] Start | Raw Input:",
      "| Seating Capacity:", seatingCapacity,
      "| Engine CC:", engineCC,
      "| Weight:", weight,
      "| Usage:", usage,
      "| Area:", area,
      "| Electric:", isElectric
    );

    // ✅ แปลงค่าข้อมูลให้ถูกต้องก่อนใช้งาน
    const validatedData = normalizeInputData(seatingCapacity, engineCC, weight, usage, area, isElectric);
    seatingCapacity = validatedData.seatingCapacity;
    engineCC = validatedData.engineCC;
    weight = validatedData.weight;
    const modelYear = validatedData.modelYear;
    usage = validatedData.usage;
    area = validatedData.area;
    isElectric = validatedData.isElectric;

    // ✅ ระบุประเภทของรถ
    const vehicleType = determineVehicleType(seatingCapacity, engineCC, weight, modelYear, isElectric);
    console.log("ℹ️ [getInsuranceDetails] Determined Vehicle Type:", vehicleType);

    if (vehicleType === "unknown") {
        return { error: "ไม่สามารถระบุประเภทของรถได้" };
    }

    return { vehicleType, seatingCapacity, engineCC, weight, modelYear, usage, area };
};
