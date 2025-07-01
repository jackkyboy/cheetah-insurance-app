import create from "zustand";

export const useFormStore = create((set) => ({
  formState: {
    insured: {},
    motor: {},
    policy: {},
    drivers: [],
    beneficiaries: [],
  },
  setFormState: (section, data) =>
    set((state) => ({
      formState: {
        ...state.formState,
        [section]: data,
      },
    })),
}));
