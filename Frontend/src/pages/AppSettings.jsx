import ThemeSwitcher from "../components/ThemeSwitcher";
import FontSelector from "../components/FontSelector";

const AppSettings = () => {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Application Settings</h1>
      <ThemeSwitcher />
      <FontSelector />
    </div>
  );
};

export default AppSettings;
