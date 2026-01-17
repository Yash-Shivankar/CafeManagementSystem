import { createSlice } from "@reduxjs/toolkit";
import { fontMap } from "../config/fonts";

const savedTheme = localStorage.getItem("theme") || "light";
const savedFont = localStorage.getItem("font") || "Inter";

const initialState = {
  theme: savedTheme,
  font: savedFont,
};

const settingsSlice = createSlice({
  name: "settings",
  initialState,
  reducers: {
    setTheme: (state, action) => {
      state.theme = action.payload;
      localStorage.setItem("theme", action.payload);
    },

    setFont: (state, action) => {
      const fontKey = action.payload;
      state.font = fontKey;
      localStorage.setItem("font", fontKey);

      const fontValue = fontMap[fontKey];
      if (fontValue) {
        document.documentElement.style.setProperty("--font-base", fontValue);
      }
    },
  },
});

export const { setTheme, setFont } = settingsSlice.actions;
export default settingsSlice.reducer;
