import { createSlice } from "@reduxjs/toolkit";
import { fontMap } from "../config/fonts";

const initialState = {
  theme: "light",
  font: "Inter",
  loading: false,
  error: null,
};

const settingsSlice = createSlice({
  name: "settings",
  initialState,
  reducers: {
    setTheme: (state, action) => {
      state.theme = action.payload;
    },

    setFont: (state, action) => {
      const fontKey = action.payload;
      state.font = fontKey;

      const fontValue = fontMap[fontKey];
      if (fontValue) {
        document.documentElement.style.setProperty("--font-base", fontValue);
      }
    },

    // Loading state handlers
    settingsLoading: (state) => {
      state.loading = true;
      state.error = null;
    },

    settingsSuccess: (state, action) => {
      state.loading = false;
      state.error = null;
      state.theme = action.payload.theme;
      state.font = action.payload.font;
    },

    settingsError: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
  },
});

export const {
  setTheme,
  setFont,
  settingsLoading,
  settingsSuccess,
  settingsError,
} = settingsSlice.actions;

export default settingsSlice.reducer;
