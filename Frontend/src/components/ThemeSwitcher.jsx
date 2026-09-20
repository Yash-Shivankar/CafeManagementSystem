import { useDispatch, useSelector } from "react-redux";
import { toast } from "react-toastify";
import { useUpdateSettingMutation } from "../app/allSlices";
import { setTheme } from "../app/settingsSlice";
import { themes, themeLabels, deriveTokens } from "../config/themes";

const rgb = (triple) => "rgb(" + triple + ")";

const ThemeSwitcher = () => {
  const dispatch = useDispatch();
  const theme = useSelector((state) => state.settings.theme);
  const [updateSetting, { isLoading }] = useUpdateSettingMutation();

  const choose = async (key) => {
    const previous = theme;
    dispatch(setTheme(key));

    try {
      await updateSetting({ key: "theme", value: key }).unwrap();
    } catch (error) {
      dispatch(setTheme(previous));
      toast.error(error?.data?.detail || "Could not save the theme");
    }
  };

  return (
    <fieldset disabled={isLoading} className="space-y-3">
      <legend className="text-sm font-semibold text-foreground">Theme</legend>
      <p className="text-xs text-muted-foreground">
        Applies to everyone signed in to this installation.
      </p>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {Object.entries(themes).map(([key, palette]) => {
          const tokens = deriveTokens(palette);
          const selected = key === theme;

          return (
            <button
              key={key}
              type="button"
              onClick={() => choose(key)}
              aria-pressed={selected}
              className={
                "rounded-md border p-3 text-left transition " +
                (selected
                  ? "border-primary ring-2 ring-primary"
                  : "border-border hover:border-primary")
              }
              style={{
                backgroundColor: rgb(palette["--color-background"]),
                color: rgb(tokens["--color-foreground"]),
              }}
            >
              <span className="flex gap-1" aria-hidden="true">
                {["primary", "secondary", "accent"].map((slot) => (
                  <span
                    key={slot}
                    className="h-4 w-4 rounded-full"
                    style={{ backgroundColor: rgb(palette["--color-" + slot]) }}
                  />
                ))}
              </span>
              <span className="mt-2 block text-xs font-medium">
                {themeLabels[key] ?? key}
              </span>
            </button>
          );
        })}
      </div>
    </fieldset>
  );
};

export default ThemeSwitcher;
