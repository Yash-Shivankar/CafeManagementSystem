const FilterBar = ({ filters, values, onChange }) => {
  return (
    <div className="flex flex-wrap gap-4 mb-4">
      {filters.map((filter) => {
        if (filter.type === "text") {
          return (
            <input
              key={filter.name}
              type="text"
              placeholder={filter.placeholder}
              value={values[filter.name] || ""}
              onChange={(e) => onChange(filter.name, e.target.value)}
              className="px-3 py-2 border border-border rounded-md"
            />
          );
        }

        if (filter.type === "select") {
          return (
            <select
              key={filter.name}
              value={values[filter.name] || ""}
              onChange={(e) => onChange(filter.name, e.target.value)}
              className="px-3 py-2 border border-border rounded-md"
            >
              <option value="">All</option>
              {filter.options.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          );
        }

        if (filter.type === "date") {
          return (
            <input
              key={filter.name}
              type="date"
              value={values[filter.name] || ""}
              onChange={(e) => onChange(filter.name, e.target.value)}
              className="px-3 py-2 border border-border rounded-md"
            />
          );
        }

        return null;
      })}
    </div>
  );
};

export default FilterBar;
