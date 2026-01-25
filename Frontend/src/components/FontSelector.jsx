import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  useGetSettingsQuery,
  useCreateSettingMutation,
  useUpdateSettingMutation,
} from "../app/allSlices";
import { setFont } from "../app/settingsSlice";
import { fontMap } from "../config/fonts";

const FontSelector = () => {
  const dispatch = useDispatch();
  const font = useSelector((state) => state.settings.font);

  const { data: settingsData, isLoading } = useGetSettingsQuery();
  const [createSetting] = useCreateSettingMutation();
  const [updateSetting] = useUpdateSettingMutation();

  // Set initial font from backend
  useEffect(() => {
    if (isLoading) return; // avoid running while loading

    const fontSetting = settingsData?.find((s) => s.key === "font");

    if (fontSetting?.value) {
      dispatch(setFont(fontSetting.value));
    } else if (!fontSetting) {
      // create default only if not exists
      createSetting({ key: "font", value: "Inter" });
      dispatch(setFont("Inter"));
    }
  }, [settingsData, isLoading, dispatch, createSetting]);

  const handleChange = async (e) => {
    const value = e.target.value;
    dispatch(setFont(value));

    const fontSetting = settingsData?.find((s) => s.key === "font");

    if (fontSetting) {
      await updateSetting({ key: "font", value }).unwrap();
    } else {
      await createSetting({ key: "font", value }).unwrap();
    }
  };

  return (
    <div className="flex flex-col space-y-2">
      <label className="font-semibold text-text">Select Font</label>
      <select
        value={font}
        onChange={handleChange}
        className="bg-surface text-text px-3 py-2 rounded-md w-60 border border-border focus:outline-none focus:ring-2 focus:ring-primary"
      >
        {Object.keys(fontMap).map((fontKey) => (
          <option
            key={fontKey}
            value={fontKey}
            className="bg-surface text-text"
          >
            {fontKey.replace(/([A-Z])/g, " $1").trim()}
          </option>
        ))}
      </select>
    </div>
  );
};

export default FontSelector;
