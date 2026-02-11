import { useState } from "react";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import { toast } from "react-toastify";

import {
  useGetEarningsQuery,
  useCreateEarningMutation,
  useUpdateEarningMutation,
  useDeleteEarningMutation,
} from "../../app/allSlices";

const Earnings = () => {
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingEarning, setEditingEarning] = useState(null);

  const limit = 10;

  const { data, isLoading, refetch } = useGetEarningsQuery({ page, limit });

  const [createEarning] = useCreateEarningMutation();
  const [updateEarning] = useUpdateEarningMutation();
  const [deleteEarning] = useDeleteEarningMutation();

  const columns = [
    { key: "id", label: "Id" },

    {
      key: "date",
      label: "Date",
      render: (value) =>
        new Date(value).toLocaleDateString("en-GB", {
          day: "2-digit",
          month: "short",
          year: "numeric",
        }),
    },

    {
      key: "revenue",
      label: "Revenue",
      render: (v) => `₹ ${Number(v).toFixed(2)}`,
    },

    {
      key: "expenses",
      label: "Expenses",
      render: (v) => `₹ ${Number(v).toFixed(2)}`,
    },

    {
      key: "profit",
      label: "Profit / Loss",
      render: (v) => (
        <span
          className={
            v < 0
              ? "text-red-600 font-semibold"
              : "text-green-600 font-semibold"
          }
        >
          ₹ {Number(v).toFixed(2)}
        </span>
      ),
    },
  ];

  const earningFormFields = [
    {
      name: "date",
      label: "Date",
      type: "date",
      required: true,
    },
    {
      name: "revenue",
      label: "Revenue",
      type: "number",
      min: 0,
      step: "0.01",
      required: true,
    },
    {
      name: "expenses",
      label: "Expenses",
      type: "number",
      min: 0,
      step: "0.01",
      required: true,
    },
  ];

  const handleSubmit = async (formData) => {
    try {
      if (editingEarning) {
        await updateEarning({
          id: editingEarning.id,
          ...formData,
        }).unwrap();
        toast.success("Earning updated successfully");
      } else {
        await createEarning(formData).unwrap();
        toast.success("Earning created successfully");
      }
      refetch();
      setShowForm(false);
      setEditingEarning(null);
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  const handleDelete = async (row) => {
    if (!window.confirm("Are you sure you want to delete this earning?"))
      return;

    try {
      await deleteEarning(row.id).unwrap();
      toast.success("Earning deleted successfully");
      refetch();
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Earnings</h1>
        <Button label="Add Earning" onClick={() => setShowForm(true)} />
      </div>

      <DataTable
        loading={isLoading}
        data={data?.data || []}
        columns={columns}
        onEdit={(row) => {
          setEditingEarning(row);
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
          title={editingEarning ? "Edit Earning" : "Create Earning"}
          onClose={() => {
            setShowForm(false);
            setEditingEarning(null);
          }}
        >
          <DynamicForm
            fields={earningFormFields}
            initialValues={editingEarning ? editingEarning : {}}
            onSubmit={handleSubmit}
          />
        </Modal>
      )}
    </div>
  );
};

export default Earnings;
