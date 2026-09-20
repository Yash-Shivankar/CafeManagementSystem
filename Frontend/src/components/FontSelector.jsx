import { useDispatch, useSelector } from "react-redux";
import { toast } from "react-toastify";
import { useUpdateSettingMutation } from "../app/allSlices";
import { setFont } from "../app/settingsSlice";
import { fontGroups, fontLabel, fontMap, loadAllFonts } from "../config/fonts";

const FontSelector = () => {
  const dispatch = useDispatch();
  const font = useSelector((state) => state.settings.font);
  const [updateSetting, { isLoading }] = useUpdateSettingMutation();

  const choose = async (value) => {
    const previous = font;
    dispatch(setFont(value));

    try {
      await updateSetting({ key: "font", value }).unwrap();
    } catch (error) {
      dispatch(setFont(previous));
      toast.error(error?.data?.detail || "Could not save the font");
    }
  };

  return (
    <div className="space-y-3">
      <label
        htmlFor="font-select"
        className="block text-sm font-semibold text-foreground"
      >
        Font
      </label>

      <select
        id="font-select"
        value={font}
        disabled={isLoading}
        onFocus={loadAllFonts}
        onMouseEnter={loadAllFonts}
        onChange={(event) => choose(event.target.value)}
        className="w-full max-w-sm rounded-md border border-border bg-surface px-3 py-2 text-foreground"
      >
        {fontGroups.map((group) => (
          <optgroup key={group.label} label={group.label}>
            {group.fonts.map((name) => (
              <option
                key={name}
                value={name}
                style={{ fontFamily: fontMap[name] }}
              >
                {fontLabel(name)}
              </option>
            ))}
          </optgroup>
        ))}
      </select>

      <p className="rounded-md border border-border bg-surface px-4 py-3 text-lg text-foreground">
        {"The quick brown fox jumps over the lazy dog — ₹1,240.50"}
      </p>
    </div>
  );
};

export default FontSelector;
