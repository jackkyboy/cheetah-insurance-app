///Users/apichet/Downloads/cheetah-insurance-app/src/components/FormContext.jsx
import React, { createContext, useState } from "react";

export const FormContext = createContext();

export const FormProvider = ({ children }) => {
  const [formState, setFormState] = useState({
    insured: {},
    motor: {},
    policy: {},
    drivers: [],
    beneficiaries: [],
  });

  const updateFormSection = (section, field, value, index = null) => {
    setFormState((prevState) => {
      if (index !== null) {
        // Update specific index in an array section (e.g., drivers or beneficiaries)
        const updatedArray = [...prevState[section]];
        updatedArray[index] = { ...updatedArray[index], [field]: value };
        return { ...prevState, [section]: updatedArray };
      }
      // Update a field in a non-array section
      return {
        ...prevState,
        [section]: { ...prevState[section], [field]: value },
      };
    });
  };

  const addArrayItem = (section, newItem) => {
    setFormState((prevState) => ({
      ...prevState,
      [section]: [...prevState[section], newItem],
    }));
  };

  const removeArrayItem = (section, index) => {
    setFormState((prevState) => ({
      ...prevState,
      [section]: prevState[section].filter((_, i) => i !== index),
    }));
  };

  return (
    <FormContext.Provider
      value={{
        formState,
        setFormState,
        updateFormSection,
        addArrayItem,
        removeArrayItem,
      }}
    >
      {children}
    </FormContext.Provider>
  );
};
