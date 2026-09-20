import { useState } from "react";
import DataTable from "../../components/DataTable";
import { useGetInventoryLogsQuery } from "../../app/allSlices";
import { formatDateTime, formatQuantity } from "../../utils/format";

const InventoryLogs = () => {
  const [page, setPage] = useState(1);
  const limit = 10;

  const { data, isLoading } = useGetInventoryLogsQuery({ page, limit });

  const columns = [
    { key: "id", label: "Id" },
    { key: "item", label: "Item", render: (item) => item?.name || "-" },
    { key: "change_type", label: "Change Type" },
    {
      key: "quantity",
      label: "Quantity",
      render: (value) => formatQuantity(value),
    },
    { key: "reference", label: "Reference" },
    {
      key: "changed_on",
      label: "Changed On",
      render: (value) => formatDateTime(value),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-foreground">Stock movements</h1>
      </div>

      <DataTable
        loading={isLoading}
        data={data?.data || []}
        columns={columns}
        caption="Inventory stock movements"
        emptyMessage="No stock movements yet"
        emptyHint="Movements appear here whenever stock is received, consumed or adjusted. This ledger is append-only — a mistake is corrected with an opposite entry."
        pagination={{
          currentPage: data?.currentPage || page,
          totalPages: data?.totalPages || 1,
          total: data?.total,
        }}
        onPageChange={setPage}
      />
    </div>
  );
};

export default InventoryLogs;
