import { useEffect, useMemo, useState } from "react";
import { useDispatch } from "react-redux";

import DataTable from "../components/DataTable";
import {
  useGetSettingsQuery,
  useCreateSettingMutation,
  useUpdateSettingMutation,
} from "../app/allSlices";
import { setTheme, setFont } from "../app/settingsSlice";
import { themes } from "../config/themes";
import { fontMap } from "../config/fonts";

const AppSettings = () => {
  const dispatch = useDispatch();

  const { data: settingsData = [], isLoading } = useGetSettingsQuery();
  const [createSetting] = useCreateSettingMutation();
  const [updateSetting] = useUpdateSettingMutation();

  const [draft, setDraft] = useState({
    theme: "",
    font: "",
  });

  useEffect(() => {
    if (isLoading) return;

    const theme =
      settingsData.find((s) => s.key === "theme")?.value || "mysticForest";
    const font = settingsData.find((s) => s.key === "font")?.value || "Inter";

    setDraft({ theme, font });
    dispatch(setTheme(theme));
    dispatch(setFont(font));
  }, [settingsData, isLoading, dispatch]);

  const handleChange = (key, value) => {
    setDraft((prev) => ({ ...prev, [key]: value }));
  };

  const saveRow = async (key) => {
    const value = draft[key];
    const existing = settingsData.find((s) => s.key === key);

    if (existing) {
      await updateSetting({ key, value }).unwrap();
    } else {
      await createSetting({ key, value }).unwrap();
    }

    if (key === "theme") dispatch(setTheme(value));
    if (key === "font") dispatch(setFont(value));
  };

  const tableData = useMemo(
    () => [
      {
        key: "theme",
        label: "Theme",
        value: draft.theme,
      },
      {
        key: "font",
        label: "Font",
        value: draft.font,
      },
    ],
    [draft],
  );

  const columns = useMemo(
    () => [
      {
        key: "label",
        label: "Setting",
      },
      {
        key: "value",
        label: "Value",
        render: (value, row) => {
          if (row.key === "theme") {
            return (
              <select
                value={value}
                onChange={(e) => handleChange("theme", e.target.value)}
                className="bg-surface text-text px-3 py-2 rounded-md w-60 border border-border"
              >
                {Object.keys(themes).map((k) => (
                  <option key={k} value={k}>
                    {k
                      .replace(/([A-Z])/g, " $1")
                      .replace(/^./, (c) => c.toUpperCase())}
                  </option>
                ))}
              </select>
            );
          }

          if (row.key === "font") {
            return (
              <select
                value={value}
                onChange={(e) => handleChange("font", e.target.value)}
                className="bg-surface text-text px-3 py-2 rounded-md w-60 border border-border"
              >
                {Object.keys(fontMap).map((k) => (
                  <option key={k} value={k}>
                    {k.replace(/([A-Z])/g, " $1").trim()}
                  </option>
                ))}
              </select>
            );
          }

          return value;
        },
      },
    ],
    [draft],
  );

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Application Settings</h1>

      <DataTable
        data={tableData}
        columns={columns}
        loading={isLoading}
        onEdit={(row) => saveRow(row.key)}
      />
    </div>
  );
};

export default AppSettings;
