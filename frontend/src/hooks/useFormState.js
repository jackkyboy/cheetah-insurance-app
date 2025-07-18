import { useContext } from "react";
import { FormContext } from "../store/formStore";

export const useFormState = () => {
  const { formState, setFormState } = useContext(FormContext);

  const updateFormState = (section, field, value) => {
    setFormState((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value,
      },
    }));
  };

  return { formState, updateFormState };
};
