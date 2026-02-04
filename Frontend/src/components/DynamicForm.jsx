import React from "react";
import Button from "../components/Button";

const DynamicForm = ({ fields, initialValues = {}, onSubmit }) => {
  const [form, setForm] = React.useState(initialValues);

  const handleChange = (name, value) => {
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const inputClass = `
    w-full px-2.5 py-1.5 rounded-md
    bg-background text-foreground
    border border-border
    focus:outline-none
    focus:ring-1 focus:ring-primary
    focus:border-primary
    placeholder:text-muted-foreground
    text-sm
  `;

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(form);
      }}
      className="space-y-2"
    >
      {fields.map((field) => (
        <div key={field.name} className="space-y-0.5">
          <label className="text-xs font-medium text-foreground">
            {field.label}
          </label>

          {field.type === "select" ? (
            <select
              value={form[field.name] ?? ""}
              onChange={(e) => handleChange(field.name, e.target.value)}
              className={inputClass}
            >
              <option value="">Select</option>
              {field.options?.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          ) : field.type === "file" ? (
            <input
              type="file"
              onChange={(e) =>
                handleChange(field.name, e.target.files?.[0] || null)
              }
              className={inputClass}
            />
          ) : (
            <input
              type={field.type}
              value={form[field.name] ?? ""}
              onChange={(e) => handleChange(field.name, e.target.value)}
              className={inputClass}
            />
          )}
        </div>
      ))}

      <div className="pt-3 flex justify-center">
        <Button type="submit" size="sm" label="Save" />
      </div>
    </form>
  );
};

export default DynamicForm;
