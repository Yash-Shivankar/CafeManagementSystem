import { useEffect, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { themes, applyTheme } from "../config/themes";
import { fontMap } from "../config/fonts";
import { useGetSettingsQuery } from "../app/allSlices";
import { settingsSuccess } from "../app/settingsSlice";
import { authService } from "../services/auth";
import { selectIsSignedIn } from "../app/authSlice";

const AppInitializer = ({ children }) => {
  const dispatch = useDispatch();
  const theme = useSelector((state) => state.settings.theme);
  const font = useSelector((state) => state.settings.font);

  const [sessionChecked, setSessionChecked] = useState(false);

  useEffect(() => {
    let cancelled = false;
    authService.bootstrap().finally(() => {
      if (!cancelled) setSessionChecked(true);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const isSignedIn = useSelector(selectIsSignedIn);

  const { data: settingsData, isLoading } = useGetSettingsQuery(undefined, {
    skip: !sessionChecked || !isSignedIn,
  });

  useEffect(() => {
    if (!isLoading && settingsData) {
      const rows = Array.isArray(settingsData)
        ? settingsData
        : (settingsData?.data ?? []);
      const themeSetting = rows.find((s) => s.key === "theme");
      const fontSetting = rows.find((s) => s.key === "font");

      dispatch(
        settingsSuccess({
          theme: themeSetting?.value || "mysticForest",
          font: fontSetting?.value || "Inter",
        }),
      );
    }
  }, [settingsData, isLoading, dispatch]);

  useEffect(() => {
    const fallbackTheme = "mysticForest";
    const activeTheme = theme && themes[theme] ? theme : fallbackTheme;

    if (themes[activeTheme]) {
      applyTheme(themes[activeTheme]);
    }

    const activeFont = font && fontMap[font] ? fontMap[font] : fontMap.Inter;
    document.documentElement.style.setProperty("--font-base", activeFont);
  }, [theme, font]);

  if (!sessionChecked) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{
          backgroundColor: "rgb(var(--color-background))",
          color: "rgb(var(--color-text-primary))",
        }}
      >
        <span className="text-sm opacity-70">Loading Caelum…</span>
      </div>
    );
  }

  return <>{children}</>;
};

export default AppInitializer;
