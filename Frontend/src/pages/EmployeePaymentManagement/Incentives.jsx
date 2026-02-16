import { useState } from "react";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import { toast } from "react-toastify";

import {
  useGetIncentivesQuery,
  useCreateIncentiveMutation,
  useUpdateIncentiveMutation,
  useDeleteIncentiveMutation,
  useGetEmployeeDetailsQuery,
} from "../../app/allSlices";

const Incentives = () => {
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingIncentive, setEditingIncentive] = useState(null);

  const limit = 10;

  const { data, isLoading, refetch } = useGetIncentivesQuery({ page, limit });
  const { data: detailsData } = useGetEmployeeDetailsQuery();

  const [createIncentive] = useCreateIncentiveMutation();
  const [updateIncentive] = useUpdateIncentiveMutation();
  const [deleteIncentive] = useDeleteIncentiveMutation();

  const columns = [
    { key: "id", label: "Id" },
    {
      key: "employee",
      label: "Employee",
      render: (employee) =>
        `${employee?.user?.first_name ?? ""} ${employee?.user?.last_name ?? ""}`.trim(),
    },
    {
      key: "type",
      label: "Incentive Type",
      render: (value) => value?.toUpperCase(),
    },
    {
      key: "amount",
      label: "Amount",
      render: (value) => `₹ ${Number(value).toFixed(2)}`,
    },
    {
      key: "date_given",
      label: "Date",
      render: (value) =>
        new Date(value).toLocaleDateString("en-GB", {
          day: "2-digit",
          month: "short",
          year: "numeric",
        }),
    },
  ];

  const incentiveFormFields = [
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
      name: "type",
      label: "Incentive Type",
      type: "select",
      required: true,
      options: [
        { label: "Daily", value: "daily" },
        { label: "Monthly", value: "monthly" },
        { label: "Annual", value: "annual" },
        { label: "Performance", value: "performance" },
      ],
    },
    {
      name: "amount",
      label: "Amount",
      type: "number",
      required: true,
      step: "0.01",
      min: 0,
    },
  ];

  const handleSubmit = async (formData) => {
    try {
      if (editingIncentive) {
        await updateIncentive({
          id: editingIncentive.id,
          ...formData,
        }).unwrap();
        toast.success("Incentive updated successfully");
      } else {
        await createIncentive(formData).unwrap();
        toast.success("Incentive created successfully");
      }
      refetch();
      setShowForm(false);
      setEditingIncentive(null);
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  const handleDelete = async (row) => {
    if (!window.confirm("Are you sure you want to delete this incentive?"))
      return;

    try {
      await deleteIncentive(row.id).unwrap();
      toast.success("Incentive deleted successfully");
      refetch();
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Incentives</h1>
        <Button label="Add Incentive" onClick={() => setShowForm(true)} />
      </div>

      <DataTable
        loading={isLoading}
        data={data?.data || []}
        columns={columns}
        onEdit={(row) => {
          setEditingIncentive(row);
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
          title={editingIncentive ? "Edit Incentive" : "Create Incentive"}
          onClose={() => {
            setShowForm(false);
            setEditingIncentive(null);
          }}
        >
          <DynamicForm
            fields={incentiveFormFields}
            initialValues={editingIncentive ? editingIncentive : {}}
            onSubmit={handleSubmit}
          />
        </Modal>
      )}
    </div>
  );
};

export default Incentives;
