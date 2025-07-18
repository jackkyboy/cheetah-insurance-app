// /Users/apichet/Downloads/cheetah-insurance-app/src/components/CarSelector.jsx

import React from "react";

const CarSelector = ({ options, label, onChange, value }) => {
    console.log(`Rendering ${label} with options:`, options); // Log options
    console.log(`Current value of ${label}:`, value); // Log current value

    return (
        <div>
            <label>{label}</label>
            <select onChange={(e) => {
                console.log(`${label} changed to:`, e.target.value); // Log value on change
                onChange(e);
            }} value={value}>
                <option value="">-- เลือก --</option>
                {options.map((option, index) => (
                    <option key={index} value={option}>
                        {option}
                    </option>
                ))}
            </select>
        </div>
    );
};

export default CarSelector;
