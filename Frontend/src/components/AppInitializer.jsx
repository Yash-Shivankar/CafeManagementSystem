import { useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { themes, applyTheme } from "../config/themes";
import { fontMap } from "../config/fonts";
import { useGetSettingsQuery } from "../app/allSlices";
import { settingsSuccess } from "../app/settingsSlice";

const AppInitializer = ({ children }) => {
  const dispatch = useDispatch();
  const theme = useSelector((state) => state.settings.theme);
  const font = useSelector((state) => state.settings.font);

  // Fetch settings from backend
  const { data: settingsData, isLoading } = useGetSettingsQuery();

  useEffect(() => {
    if (!isLoading && settingsData) {
      const themeSetting = settingsData.find((s) => s.key === "theme");
      const fontSetting = settingsData.find((s) => s.key === "font");

      dispatch(
        settingsSuccess({
          theme: themeSetting?.value || "mysticForest",
          font: fontSetting?.value || "Inter",
        }),
      );
    }
  }, [settingsData, isLoading, dispatch]);

  useEffect(() => {
    // ---------- THEME ----------
    const fallbackTheme = "mysticForest";
    const activeTheme = theme && themes[theme] ? theme : fallbackTheme;

    if (themes[activeTheme]) {
      applyTheme(themes[activeTheme]);
    }

    // ---------- FONT ----------
    const activeFont = font && fontMap[font] ? fontMap[font] : fontMap.Inter;
    document.documentElement.style.setProperty("--font-base", activeFont);
  }, [theme, font]);

  return <>{children}</>;
};

export default AppInitializer;
