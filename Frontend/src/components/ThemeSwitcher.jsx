import { useDispatch, useSelector } from "react-redux";
import { setTheme } from "../app/settingsSlice";
import { themes } from "../config/themes";

const ThemeSwitcher = () => {
  const dispatch = useDispatch();
  const theme = useSelector((state) => state.settings.theme);

  const handleChange = (e) => {
    dispatch(setTheme(e.target.value));
  };

  return (
    <div className="flex flex-col space-y-2">
      <label className="font-base font-semibold text-text">Select Theme</label>

      <select
        value={theme}
        onChange={handleChange}
        className="
          font-base
          bg-surface
          text-text
          px-3 py-2
          rounded-md
          w-60
          border border-border
          focus:outline-none
          focus:ring-2 focus:ring-primary
        "
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
