import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  useGetSettingsQuery,
  useCreateSettingMutation,
  useUpdateSettingMutation,
} from "../app/allSlices";
import { setTheme } from "../app/settingsSlice";
import { themes } from "../config/themes";

const ThemeSwitcher = () => {
  const dispatch = useDispatch();
  const theme = useSelector((state) => state.settings.theme);

  const { data: settingsData, isLoading } = useGetSettingsQuery();
  const [createSetting] = useCreateSettingMutation();
  const [updateSetting] = useUpdateSettingMutation();

  // Set initial theme from backend
  useEffect(() => {
    if (isLoading) return; // prevent extra calls while loading

    const themeSetting = settingsData?.find((s) => s.key === "theme");

    if (themeSetting?.value) {
      dispatch(setTheme(themeSetting.value));
    } else if (!themeSetting) {
      // create default only if not exists
      createSetting({ key: "theme", value: "mysticForest" });
      dispatch(setTheme("mysticForest"));
    }
  }, [settingsData, isLoading, dispatch, createSetting]);

  const handleChange = async (e) => {
    const value = e.target.value;
    dispatch(setTheme(value));

    const themeSetting = settingsData?.find((s) => s.key === "theme");

    if (themeSetting) {
      await updateSetting({ key: "theme", value }).unwrap();
    } else {
      await createSetting({ key: "theme", value }).unwrap();
    }
  };

  return (
    <div className="flex flex-col space-y-2">
      <label className="font-base font-semibold text-text">Select Theme</label>
      <select
        value={theme}
        onChange={handleChange}
        className="font-base bg-surface text-text px-3 py-2 rounded-md w-60 border border-border focus:outline-none focus:ring-2 focus:ring-primary"
      >
        {Object.keys(themes).map((key) => (
          <option key={key} value={key} className="bg-surface text-text">
            {key
              .replace(/([A-Z])/g, " $1")
              .replace(/^./, (c) => c.toUpperCase())}
          </option>
        ))}
      </select>
    </div>
  );
};

export default ThemeSwitcher;
