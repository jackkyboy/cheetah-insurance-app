// /Users/apichet/Downloads/cheetah-insurance-app/src/components/FallbackSuggestions.jsx

import React from "react";

const FallbackSuggestions = ({
  availableYears = [],
  insuranceTypes = [],
  insuranceCompanies = [],
  onSelect,
}) => {
  return (
    <div className="p-4 border border-gray-300 rounded-xl bg-gray-50">
      <h2 className="text-lg font-semibold mb-2 text-gray-800">
        ตัวเลือกใกล้เคียงที่เราค้นมาให้ได้
      </h2>

      {/* ปีรถที่มี */}
      {availableYears.length > 0 && (
        <div className="mb-4">
          <div className="text-gray-600 mb-1">ปีรถยนต์ที่พบ:</div>
          <div className="flex flex-wrap gap-2">
            {availableYears.map((year) => (
              <button
                key={year}
                onClick={() => onSelect("car_model_year", year)}
                className="px-3 py-1 bg-white border border-gray-300 rounded-full text-sm hover:bg-blue-100"
              >
                {year}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ประเภทประกันที่มี */}
      {insuranceTypes.length > 0 && (
        <div className="mb-4">
          <div className="text-gray-600 mb-1">ประเภทประกันที่มี:</div>
          <div className="flex flex-wrap gap-2">
            {insuranceTypes.map((type) => (
              <button
                key={type}
                onClick={() => onSelect("insurance_type", type)}
                className="px-3 py-1 bg-white border border-gray-300 rounded-full text-sm hover:bg-blue-100"
              >
                ชั้น {type}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* บริษัทประกันใกล้เคียง */}
      {insuranceCompanies.length > 0 && (
        <div>
          <div className="text-gray-600 mb-1">บริษัทประกันที่มี:</div>
          <div className="flex flex-wrap gap-2">
            {insuranceCompanies.map((company) => (
              <button
                key={company}
                onClick={() => onSelect("company_name", company)}
                className="px-3 py-1 bg-white border border-gray-300 rounded-full text-sm hover:bg-blue-100"
              >
                {company}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default FallbackSuggestions;
