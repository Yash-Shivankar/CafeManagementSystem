import Button from "./Button";

const DataTable = ({
  data = [],
  columns = [],
  onEdit,
  pagination = {},
  onPageChange,
}) => {
  if (!data || data.length === 0) return <p>No data found</p>;

  const tableColumns = columns.length
    ? columns
    : Object.keys(data[0]).map((k) => ({ key: k, label: k }));

  const { currentPage = 1, totalPages = 1 } = pagination;

  return (
    <div className="overflow-x-auto border border-border rounded-md">
      <table className="w-full border-collapse">
        <thead className="bg-background">
          <tr>
            {tableColumns.map((col) => (
              <th
                key={col.key}
                className="text-left px-4 py-2 border-b border-border"
              >
                {col.label}
              </th>
            ))}
            <th className="px-4 py-2">Actions</th>
          </tr>
        </thead>

        <tbody>
          {data.map((row, i) => (
            <tr key={i} className="hover:bg-background/50">
              {tableColumns.map((col) => (
                <td key={col.key} className="px-4 py-2 border-b border-border">
                  {col.render ? col.render(row[col.key], row) : row[col.key]}
                </td>
              ))}
              <td className="px-4 py-2">
                <Button label="Edit" size="sm" onClick={() => onEdit(row)} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Pagination */}
      <div className="flex items-center justify-between p-4">
        <div>
          Page {currentPage} of {totalPages}
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
