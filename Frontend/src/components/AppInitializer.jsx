import { useEffect } from "react";
import { useSelector } from "react-redux";
import { themes, applyTheme } from "../config/themes";
import { fontMap } from "../config/fonts";

const AppInitializer = ({ children }) => {
  const theme = useSelector((state) => state.settings.theme);
  const font = useSelector((state) => state.settings.font);

  useEffect(() => {
    /* ---------- THEME ---------- */
    const fallbackTheme = "mysticForest";
    const activeTheme = theme && themes[theme] ? theme : fallbackTheme;

    applyTheme(themes[activeTheme]);

    /* ---------- FONT ----------- */
    const activeFont = fontMap[font] || fontMap.Inter;

    document.documentElement.style.setProperty("--font-base", activeFont);
  }, [theme, font]);

  return children;
};

export default AppInitializer;
