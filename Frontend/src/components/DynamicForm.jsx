import Button from "../ui/Button";

const DynamicForm = ({ fields, initialValues = {}, onSubmit }) => {
  const [form, setForm] = React.useState(initialValues);

  const handleChange = (name, value) => {
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(form);
      }}
      className="space-y-4"
    >
      {fields.map((field) => {
        if (field.type === "select") {
          return (
            <select
              key={field.name}
              value={form[field.name] || ""}
              onChange={(e) => handleChange(field.name, e.target.value)}
              className="w-full px-3 py-2 border border-border rounded-md"
            >
              <option value="">Select {field.label}</option>
              {field.options.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          );
        }

        return (
          <input
            key={field.name}
            type={field.type}
            placeholder={field.placeholder}
            value={form[field.name] || ""}
            onChange={(e) => handleChange(field.name, e.target.value)}
            className="w-full px-3 py-2 border border-border rounded-md"
          />
        );
      })}

      <Button type="submit" label="Save" />
    </form>
  );
};

export default DynamicForm;
