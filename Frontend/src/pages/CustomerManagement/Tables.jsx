import { useState } from "react";
import { useConfirm } from "../../components/useConfirm";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import FilterBar from "../../components/FilterBar";
import { toast } from "react-toastify";

import {
  useGetTablesQuery,
  useCreateTableMutation,
  useUpdateTableMutation,
  useDeleteTableMutation,
} from "../../app/allSlices";

const Tables = () => {
  const confirm = useConfirm();
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingTable, setEditingTable] = useState(null);
  const [filters, setFilters] = useState({});
  const [appliedFilters, setAppliedFilters] = useState({});

  const limit = 10;

  const { data, isLoading, refetch } = useGetTablesQuery({
    page,
    limit,
    ...appliedFilters,
  });

  const [createTable] = useCreateTableMutation();
  const [updateTable] = useUpdateTableMutation();
  const [deleteTable] = useDeleteTableMutation();

  const tableFiltersConfig = [
    {
      name: "search",
      label: "Search",
      type: "text",
      placeholder: "Table No. / Seating Capacity",
    },
  ];

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const applyFilters = () => {
    const cleanedFilters = Object.fromEntries(
      Object.entries(filters).filter(
        ([, value]) => value !== "" && value !== null && value !== undefined,
      ),
    );

    setPage(1);
    setAppliedFilters(cleanedFilters);
  };

  const resetFilters = () => {
    setFilters({});
    setAppliedFilters({});
    setPage(1);
  };

  const columns = [
    { key: "id", label: "Id" },
    { key: "table_number", label: "Table No." },
    { key: "seating_capacity", label: "Seating Capacity" },
  ];

  const tableFormFields = [
    { name: "table_number", label: "Table No.", type: "text" },
    {
      name: "seating_capacity",
      label: "Seating Capacity",
      type: "number",
      min: 1,
      step: 1,
    },
  ];

  const handleSubmit = async (formData) => {
    try {
      if (editingTable) {
        await updateTable({
          id: editingTable.id,
          ...formData,
        }).unwrap();
        toast.success("Table updated successfully");
      } else {
        await createTable(formData).unwrap();
        toast.success("Table created successfully");
      }
      refetch();
      setShowForm(false);
      setEditingTable(null);
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  const handleDelete = async (row) => {
    if (!(await confirm({
        title: "Delete this table?",
        message:
          "It will stop appearing in lists and reports. This cannot be undone from the app.",
        tone: "danger",
        confirmLabel: "Delete",
        }))) {
      return;
    }try {
      await deleteTable(row.id).unwrap();
      toast.success("Table deleted successfully");
      refetch();
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Tables</h1>
        <Button label="Add Table" onClick={() => setShowForm(true)} />
      </div>

      <FilterBar
        filters={tableFiltersConfig}
        values={filters}
        onChange={handleFilterChange}
        onApply={applyFilters}
        onReset={resetFilters}
      />

      <DataTable
        loading={isLoading}
        data={data?.data || []}
        columns={columns}
        onEdit={(row) => {
          setEditingTable(row);
          setShowForm(true);
        }}
        onDelete={handleDelete}
        pagination={{
          currentPage: data?.currentPage || page,
          totalPages: data?.totalPages || 1,
        }}
        onPageChange={setPage}
      />

      {showForm && (
        <Modal
          title={editingTable ? "Edit Table" : "Create Table"}
          onClose={() => {
            setShowForm(false);
            setEditingTable(null);
          }}
        >
          <DynamicForm
            fields={tableFormFields}
            initialValues={editingTable ? editingTable : {}}
            onSubmit={handleSubmit}
          />
        </Modal>
      )}
    </div>
  );
};

export default Tables;
