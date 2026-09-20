import React from "react";
import Button from "./Button";
import StarInput from "./StarInput";

const DynamicForm = ({
  fields,
  initialValues = {},
  onSubmit,
  onCancel,
  submitLabel = "Save",
  submitting = false,
  errors = {},
}) => {
  const [form, setForm] = React.useState(initialValues);
  const formId = React.useId();

  const handleChange = (name, value) => {
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const declaredValues = () =>
    Object.fromEntries(
      fields
        .filter((field) => form[field.name] !== undefined)
        .map((field) => [field.name, form[field.name]]),
    );

  const inputClass = `
    w-full px-2.5 py-1.5 rounded-md
    bg-background text-foreground
    border border-border
    focus:border-primary
    placeholder:text-muted-foreground
    text-sm
  `;

  return (
    <form
      noValidate
      onSubmit={(e) => {
        e.preventDefault();
        if (submitting) return;
        onSubmit(declaredValues());
      }}
      className="space-y-2"
    >
      {fields.map((field) => {
        const id = `${formId}-${field.name}`;
        const error = errors[field.name];
        const describedBy =
          [error && `${id}-error`, field.help && `${id}-help`].filter(Boolean).join(" ") ||
          undefined;

        const common = {
          id,
          name: field.name,
          "aria-invalid": error ? true : undefined,
          "aria-describedby": describedBy,
          required: field.required || undefined,
          className: `${inputClass} ${error ? "border-error" : ""}`,
        };

        return (
          <div key={field.name} className="space-y-0.5">
            <label htmlFor={id} className="text-xs font-medium text-foreground">
              {field.label}
              {field.required && (
                <span className="text-error ml-0.5" aria-hidden="true">
                  *
                </span>
              )}
            </label>

            {field.type === "select" ? (
              <select
                {...common}
                value={form[field.name] ?? ""}
                onChange={(e) => handleChange(field.name, e.target.value)}
              >
                <option value="">Select</option>
                {field.options?.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            ) : field.type === "stars" ? (
              <StarInput
                value={form[field.name] ?? 0}
                max={field.max || 5}
                label={field.label}
                onChange={(val) => handleChange(field.name, val)}
              />
            ) : field.type === "textarea" ? (
              <textarea
                {...common}
                rows={field.rows || 3}
                placeholder={field.placeholder}
                value={form[field.name] ?? ""}
                onChange={(e) => handleChange(field.name, e.target.value)}
              />
            ) : field.type === "file" ? (
              <input
                {...common}
                type="file"
                accept={field.accept}
                onChange={(e) => handleChange(field.name, e.target.files?.[0] || null)}
              />
            ) : (
              <input
                {...common}
                type={field.type}
                placeholder={field.placeholder}
                step={field.step}
                min={field.min}
                max={field.type === "number" ? field.max : undefined}
                value={form[field.name] ?? ""}
                onChange={(e) => handleChange(field.name, e.target.value)}
              />
            )}

            {field.help && !error && (
              <p id={`${id}-help`} className="text-xs text-muted-foreground">
                {field.help}
              </p>
            )}
            {error && (
              <p id={`${id}-error`} role="alert" className="text-xs text-error">
                {error}
              </p>
            )}
          </div>
        );
      })}

      <div className="pt-3 flex justify-center gap-2">
        {onCancel && (
          <Button label="Cancel" size="sm" variant="outline" onClick={onCancel} />
        )}
        <Button type="submit" size="sm" label={submitLabel} loading={submitting} />
      </div>
    </form>
  );
};

export default DynamicForm;
