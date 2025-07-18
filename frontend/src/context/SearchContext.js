// /Users/apichet/Downloads/cheetah-insurance-app/src/context/SearchContext.js
import React, { createContext, useReducer, useContext, useMemo, useEffect } from "react";

const SearchContext = createContext();

const initialState = {
  results: [],
  page: 1,
  totalPages: 1,
  filters: {}, // Added filters to the state
};

const ACTIONS = {
  SAVE_SEARCH_RESULTS: "SAVE_SEARCH_RESULTS",
  RESET_SEARCH: "RESET_SEARCH",
  LOAD_PREVIOUS_SEARCH: "LOAD_PREVIOUS_SEARCH",
  UPDATE_FILTERS: "UPDATE_FILTERS",
};

const reducer = (state, action) => {
  switch (action.type) {
    case ACTIONS.SAVE_SEARCH_RESULTS:
      if (!action.payload || !action.payload.results) {
        console.error("❌ Invalid payload for SAVE_SEARCH_RESULTS:", action.payload);
        return state;
      }
      return {
        ...state,
        results: action.payload.results,
        page: action.payload.page || 1,
        totalPages: action.payload.total_pages || 1,
      };
    case ACTIONS.RESET_SEARCH:
      return initialState;
    case ACTIONS.LOAD_PREVIOUS_SEARCH:
      const previousState = JSON.parse(localStorage.getItem("previousSearch")) || initialState;
      return { ...state, ...previousState };
    case ACTIONS.UPDATE_FILTERS:
      return {
        ...state,
        filters: { ...state.filters, ...action.payload },
      };
    default:
      console.warn("⚠️ Unknown action type:", action.type);
      return state;
  }
};

export const SearchProvider = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, initialState);

  // Save state to localStorage
  useEffect(() => {
    localStorage.setItem("previousSearch", JSON.stringify(state));
  }, [state]);

  // Memoize context value
  const value = useMemo(() => ({ state, dispatch }), [state, dispatch]);

  // Debug log for state changes
  useEffect(() => {
    console.log("🔍 Current Search State:", state);
  }, [state]);

  return <SearchContext.Provider value={value}>{children}</SearchContext.Provider>;
};

export const useSearch = () => {
  const context = useContext(SearchContext);
  if (!context) {
    throw new Error("useSearch must be used within a SearchProvider");
  }
  return context;
};
