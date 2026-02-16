import { useState } from "react";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import { toast } from "react-toastify";

import {
  useGetInventoryLogsQuery,
  useGetInventoryItemsQuery,
} from "../../app/allSlices";

const InventoryLogs = () => {
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingLog, setEditingLog] = useState(null);

  const limit = 10;

  const { data, isLoading, refetch } = useGetInventoryLogsQuery({
    page,
    limit,
  });
  const { data: itemsData } = useGetInventoryItemsQuery();

  const columns = [
    { key: "id", label: "Id" },
    { key: "item", label: "Item", render: (item) => item?.name || "-" },
    { key: "change_type", label: "Change Type" },
    { key: "quantity", label: "Quantity" },
    { key: "reference", label: "Reference" },
    { key: "changed_on", label: "Changed On" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Logs</h1>
      </div>

      <DataTable
        loading={isLoading}
        data={data?.data || []}
        columns={columns}
        pagination={{
          currentPage: data?.currentPage || page,
          totalPages: data?.totalPages || 1,
        }}
        onPageChange={setPage}
      />
    </div>
  );
};

export default InventoryLogs;
