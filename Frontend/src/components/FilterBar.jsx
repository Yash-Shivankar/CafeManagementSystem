const FilterBar = ({ filters, values, onChange, onApply, onReset }) => {
  return (
    <div className="w-full mb-4">
      <div className="flex flex-wrap gap-4 items-end w-full">

        <div className="flex flex-wrap gap-4 flex-1">
          {filters.map((filter) => {
            const label = filter.label;

            if (filter.type === "text") {
              return (
                <div
                  key={filter.name}
                  className="flex flex-col gap-1 flex-1 min-w-[220px]"
                >
                  <label className="text-xs font-medium text-muted-foreground">{label}</label>

                  <input
                    type="text"
                    placeholder={filter.placeholder}
                    value={values[filter.name] ?? ""}
                    onChange={(e) => onChange(filter.name, e.target.value)}
                    className="
                      h-10 px-4 rounded-md
                      bg-surface text-foreground placeholder:text-muted-foreground
                      border border-border
                      focus:outline-none focus:ring-2 focus:ring-primary
                      transition
                    "
                  />
                </div>
              );
            }

            if (filter.type === "select") {
              return (
                <div
                  key={filter.name}
                  className="flex flex-col gap-1 min-w-[160px]"
                >
                  <label className="text-xs font-medium text-muted-foreground">{label}</label>

                  <select
                    value={values[filter.name] ?? ""}
                    onChange={(e) => onChange(filter.name, e.target.value)}
                    className="
                      h-10 px-4 rounded-md
                      bg-surface text-foreground
                      border border-border
                      focus:outline-none focus:ring-2 focus:ring-primary
                      transition
                    "
                  >
                    <option value="">All</option>
                    {filter.options.map((opt) =>
                      typeof opt === "object" ? (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ) : (
                        <option key={opt} value={opt}>
                          {opt}
                        </option>
                      ),
                    )}
                  </select>
                </div>
              );
            }

            if (filter.type === "date") {
              return (
                <div
                  key={filter.name}
                  className="flex flex-col gap-1 min-w-[160px]"
                >
                  <label className="text-xs font-medium text-muted-foreground">{label}</label>

                  <input
                    type="date"
                    value={values[filter.name] ?? ""}
                    onChange={(e) => onChange(filter.name, e.target.value)}
                    className="
                      h-10 px-4 rounded-md
                      bg-surface text-foreground
                      border border-border
                      focus:outline-none focus:ring-2 focus:ring-primary
                      transition
                    "
                  />
                </div>
              );
            }

            return null;
          })}
        </div>

        {(onApply || onReset) && (
          <div className="flex gap-2 ml-auto">
            {onApply && (
              <button
                onClick={onApply}
                className="
                  h-10 px-5 rounded-md
                  bg-primary text-on-primary
                  hover:bg-primary-dark
                  transition
                "
              >
                Apply
              </button>
            )}

            {onReset && (
              <button
                onClick={onReset}
                className="
                  h-10 px-5 rounded-md
                  border border-border
                  text-foreground
                  hover:bg-muted
                  transition
                "
              >
                Reset
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default FilterBar;
