import { useState } from "react";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import { toast } from "react-toastify";

import {
  useGetIncrementHistoriesQuery,
  useCreateIncrementHistoryMutation,
  useUpdateIncrementHistoryMutation,
  useDeleteIncrementHistoryMutation,
  useGetEmployeeDetailsQuery,
} from "../../app/allSlices";

const Increments = () => {
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingIncrement, setEditingIncrement] = useState(null);

  const limit = 10;

  const { data, isLoading, refetch } = useGetIncrementHistoriesQuery({
    page,
    limit,
  });
  const { data: detailsData } = useGetEmployeeDetailsQuery();

  const [createIncrement] = useCreateIncrementHistoryMutation();
  const [updateIncrement] = useUpdateIncrementHistoryMutation();
  const [deleteIncrement] = useDeleteIncrementHistoryMutation();

  const columns = [
    { key: "id", label: "Id" },
    {
      key: "employee",
      label: "Employee",
      render: (employee) =>
        `${employee?.user?.first_name ?? ""} ${employee?.user?.last_name ?? ""}`.trim(),
    },
    {
      key: "old_package",
      label: "Old Package",
      render: (value) => {
        if (!value) return "-";
        return `₹ ${Number(value).toFixed(2)} LPA`;
      },
    },
    {
      key: "new_package",
      label: "New Package",
      render: (value) => {
        if (!value) return "-";
        return `₹ ${Number(value).toFixed(2)} LPA`;
      },
    },
    {
      key: "increment_percentage",
      label: "Increment %",
      render: (value) => `${value}%`,
    },
    {
      key: "increment_date",
      label: "Increment Date",
      render: (value) =>
        new Date(value).toLocaleDateString("en-GB", {
          day: "2-digit",
          month: "short",
          year: "numeric",
        }),
    },
  ];

  const incrementFormFields = [
    {
      name: "employee_id",
      label: "Employee",
      type: "select",
      required: true,
      options:
        detailsData?.data?.map((u) => ({
          label:
            `${u?.user?.first_name || ""} ${u?.user?.last_name || ""}`.trim(),
          value: u.id,
        })) || [],
    },
    {
      name: "old_package",
      label: "Old Package",
      type: "number",
      required: true,
      step: "0.01",
      min: 0,
    },
    {
      name: "increment_percentage",
      label: "Increment Percentage",
      type: "number",
      required: true,
      step: "0.01",
      min: 0,
    },
  ];

  const handleSubmit = async (formData) => {
    try {
      if (editingIncrement) {
        await updateIncrement({
          id: editingIncrement.id,
          ...formData,
        }).unwrap();
        toast.success("Increment updated successfully");
      } else {
        await createIncrement(formData).unwrap();
        toast.success("Increment created successfully");
      }
      refetch();
      setShowForm(false);
      setEditingIncrement(null);
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  const handleDelete = async (row) => {
    if (!window.confirm("Are you sure you want to delete this increment?"))
      return;

    try {
      await deleteIncrement(row.id).unwrap();
      toast.success("Increment deleted successfully");
      refetch();
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Increments</h1>
        <Button label="Add Increment" onClick={() => setShowForm(true)} />
      </div>

      <DataTable
        loading={isLoading}
        data={data?.data || []}
        columns={columns}
        onEdit={(row) => {
          setEditingIncrement(row);
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
          title={editingIncrement ? "Edit Increment" : "Create Increment"}
          onClose={() => {
            setShowForm(false);
            setEditingIncrement(null);
          }}
        >
          <DynamicForm
            fields={incrementFormFields}
            initialValues={editingIncrement ? editingIncrement : {}}
            onSubmit={handleSubmit}
          />
        </Modal>
      )}
    </div>
  );
};

export default Increments;
