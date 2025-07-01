// /Users/apichet/Downloads/cheetah-insurance-app/src/api/carLogos.js

// Mapping โลโก้แบรนด์รถยนต์กับโลโก้ในโฟลเดอร์ assets
const carLogos = {
    "mg": "/assets/car-logos/logos/thumb/mg.png",
    "brabus": "/assets/car-logos/logos/thumb/brabus.png",
    "chery": "/assets/car-logos/logos/thumb/chery.png",
    "citroen": "/assets/car-logos/logos/thumb/citroen.png",
    "ferrari": "/assets/car-logos/logos/thumb/ferrari.png",
    "subaru": "/assets/car-logos/logos/thumb/subaru.png",
    "volkswagen": "/assets/car-logos/logos/thumb/volkswagen.png",
    "range rover": "/assets/car-logos/logos/thumb/land-rover.png", // โลโก้ Range Rover ใช้ร่วมกับ Land Rover
    "jaguar": "/assets/car-logos/logos/thumb/jaguar.png",
    "peugeot": "/assets/car-logos/logos/thumb/peugeot.png",
    "fiat": "/assets/car-logos/logos/thumb/fiat.png",
    "rover": "/assets/car-logos/logos/thumb/rover.png",
    "porsche": "/assets/car-logos/logos/thumb/porsche.png",
    "saab": "/assets/car-logos/logos/thumb/saab.png",
    "suzuki": "/assets/car-logos/logos/thumb/suzuki.png",
    "aston martin": "/assets/car-logos/logos/thumb/aston-martin.png",
    "hyundai": "/assets/car-logos/logos/thumb/hyundai.png",
    "fomm": "/assets/car-logos/logos/thumb/default-logo.png", // ไม่มีโลโก้ใน dataset
    "mclaren": "/assets/car-logos/logos/thumb/mclaren.png",
    "byd": "/assets/car-logos/logos/thumb/byd.png",
    "thairung": "/assets/car-logos/logos/thumb/default-logo.png", // ไม่มีโลโก้ใน dataset
    "mazda": "/assets/car-logos/logos/thumb/mazda.png",
    "mini": "/assets/car-logos/logos/thumb/mini.png",
    "audi": "/assets/car-logos/logos/thumb/audi.png",
    "mercedes-benz": "/assets/car-logos/logos/thumb/mercedes-benz.png",
    "alfa": "/assets/car-logos/logos/thumb/alfa-romeo.png", // Alfa Romeo
    "hummer": "/assets/car-logos/logos/thumb/hummer.png",
    "haval": "/assets/car-logos/logos/thumb/haval.png",
    "bmw": "/assets/car-logos/logos/thumb/bmw.png",
    "toyota": "/assets/car-logos/logos/thumb/toyota.png",
    "ac": "/assets/car-logos/logos/thumb/ac.png",
    "volvo": "/assets/car-logos/logos/thumb/volvo.png",
    "proton": "/assets/car-logos/logos/thumb/proton.png"
};

// ฟังก์ชันสำหรับดึงโลโก้แบรนด์รถยนต์
// ฟังก์ชันสำหรับดึงโลโก้แบรนด์รถยนต์
export const getCarLogoUrl = (brand) => {
    const normalizedBrand = brand?.toLowerCase().trim();
    const logoUrl = `/assets/car-logos/logos/thumb/${normalizedBrand}.png`;
  
    console.log(`🛠️ Checking logo URL for brand "${normalizedBrand}": ${logoUrl}`);
  
    return logoUrl || "/assets/car-logos/logos/thumb/default-logo.png"; // Default fallback
  };
  