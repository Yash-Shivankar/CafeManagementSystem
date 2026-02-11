import Button from "./Button";

const DataTable = ({
  data = [],
  columns = [],
  onEdit,
  onDelete,
  pagination = {},
  onPageChange,
  loading = false,
}) => {
  if (loading)
    return <div className="p-4 text-muted-foreground">Loading...</div>;

  if (!data || data.length === 0)
    return <div className="p-4 text-muted-foreground">No data found</div>;

  const tableColumns = columns.length
    ? columns
    : Object.keys(data[0]).map((k) => ({ key: k, label: k }));

  const { currentPage = 1, totalPages = 1 } = pagination;

  return (
    <div className="overflow-x-hidden rounded-md border border-border bg-background">
      <table className="w-full table-fixed border-collapse text-sm text-foreground">
        <thead className="bg-muted">
          <tr>
            {tableColumns.map((col) => (
              <th
                key={col.key}
                className="
                  px-4 py-3
                  text-left
                  font-semibold text-sm
                  tracking-wide
                  border-b border-border
                  text-foreground
                  bg-muted
                  uppercase
                "
              >
                {col.label}
              </th>
            ))}

            <th
              className="
                px-4 py-3
                text-center
                font-semibold text-sm
                tracking-wide
                border-b border-border
                text-foreground
                bg-muted
                uppercase
              "
            >
              Actions
            </th>
          </tr>
        </thead>

        <tbody>
          {data.map((row, i) => (
            <tr
              key={i}
              className="
                transition
                hover:bg-muted/50
              "
            >
              {tableColumns.map((col) => (
                // <td
                //   key={col.key}
                //   className="
                //     px-4 py-2
                //     border-b border-border
                //     text-foreground
                //     break-words whitespace-normal
                //     truncate max-w-[220px]
                //   "
                // >
                //   {col.render ? col.render(row[col.key], row) : row[col.key]}
                // </td>
                <td
                  key={col.key}
                  className="px-4 py-2 border-b border-border max-w-[220px]"
                >
                  <div
                    className="truncate"
                    title={col.render ? undefined : row[col.key]}
                  >
                    {col.render ? col.render(row[col.key], row) : row[col.key]}
                  </div>
                </td>
              ))}

              {/* ACTIONS */}
              <td className="px-4 py-2 border-b border-border">
                <div className="flex items-center justify-center gap-2 whitespace-nowrap">
                  <Button
                    label="Edit"
                    size="sm"
                    onClick={() => onEdit?.(row)}
                  />

                  {onDelete && (
                    <Button
                      label="Delete"
                      size="sm"
                      variant="danger"
                      onClick={() => onDelete(row)}
                    />
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Pagination */}
      <div
        className="
          flex items-center justify-between
          px-4 py-3
          border-t border-border
          text-sm text-muted-foreground
        "
      >
        <div>
          Page <span className="text-foreground">{currentPage}</span> of{" "}
          <span className="text-foreground">{totalPages}</span>
        </div>

        <div className="flex gap-2">
          <Button
            label="Prev"
            size="sm"
            disabled={currentPage === 1}
            onClick={() => onPageChange(currentPage - 1)}
          />
          <Button
            label="Next"
            size="sm"
            disabled={currentPage === totalPages}
            onClick={() => onPageChange(currentPage + 1)}
          />
        </div>
      </div>
    </div>
  );
};

export default DataTable;
