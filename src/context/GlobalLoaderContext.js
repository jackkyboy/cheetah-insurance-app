// /Users/apichet/Downloads/cheetah-insurance-app/src/context/GlobalLoaderContext.js
import React, { createContext, useState, useContext } from "react";

// Create Context
const LoaderContext = createContext();

// Provider Component
export const LoaderProvider = ({ children }) => {
  const [isLoading, setIsLoading] = useState(false);

  return (
    <LoaderContext.Provider value={{ isLoading, setIsLoading }}>
      {children}
    </LoaderContext.Provider>
  );
};

// Hook to use the Loader Context
export const useLoader = () => {
  return useContext(LoaderContext);
};
