import { useDispatch, useSelector } from "react-redux";
import { setFont } from "../app/settingsSlice";
import { fontMap } from "../config/fonts";

const FontSelector = () => {
  const dispatch = useDispatch();
  const font = useSelector((state) => state.settings.font);

  const handleChange = (e) => {
    dispatch(setFont(e.target.value));
  };

  return (
    <div className="flex flex-col space-y-2">
      <label className="font-semibold text-text">Select Font</label>

      <select
        value={font}
        onChange={handleChange}
        className="
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
