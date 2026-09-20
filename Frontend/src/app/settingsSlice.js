import { createSlice } from "@reduxjs/toolkit";
import { DEFAULT_FONT, fontMap, loadFont } from "../config/fonts";

export const DEFAULT_THEME = "mysticForest";

const initialState = {
  theme: DEFAULT_THEME,
  font: DEFAULT_FONT,
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
        loadFont(fontKey);
        document.documentElement.style.setProperty("--font-base", fontValue);
      }
    },
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
