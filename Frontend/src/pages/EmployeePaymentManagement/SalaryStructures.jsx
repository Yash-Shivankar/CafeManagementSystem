import { useState } from "react";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import { toast } from "react-toastify";

import {
  useGetSalaryStructuresQuery,
  useCreateSalaryStructureMutation,
  useUpdateSalaryStructureMutation,
  useDeleteSalaryStructureMutation,
  useGetEmployeeDetailsQuery,
} from "../../app/allSlices";

const SalaryStructures = () => {
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingStructure, setEditingStructure] = useState(null);

  const limit = 10;

  const { data, isLoading, refetch } = useGetSalaryStructuresQuery({
    page,
    limit,
  });
  const { data: detailsData } = useGetEmployeeDetailsQuery();

  const [createStructure] = useCreateSalaryStructureMutation();
  const [updateStructure] = useUpdateSalaryStructureMutation();
  const [deleteStructure] = useDeleteSalaryStructureMutation();

  const columns = [
    { key: "id", label: "ID" },
    {
      key: "employee",
      label: "Employee",
      render: (employee) =>
        `${employee?.user?.first_name ?? ""} ${employee?.user?.last_name ?? ""}`.trim(),
    },

    {
      key: "package_lpa",
      label: "Package (LPA)",
      render: (value) => {
        if (!value) return "-";
        return `₹ ${Number(value).toFixed(2)} LPA`;
      },
    },
    {
      key: "monthly_salary",
      label: "Monthly Salary",
      render: (value) => {
        if (!value) return "-";
        return `₹ ${Number(value).toFixed(2)}`;
      },
    },

    { key: "pf_percentage", label: "PF (%)", render: (value) => `${value}%` },
    { key: "esi_percentage", label: "ESI (%)", render: (value) => `${value}%` },

    {
      key: "allowances",
      label: "Allowances",
      render: (value) => {
        if (!value) return "-";
        return `₹ ${Number(value).toFixed(2)}`;
      },
    },
    {
      key: "deductions",
      label: "Deductions",
      render: (value) => {
        if (!value) return "-";
        return `₹ ${Number(value).toFixed(2)}`;
      },
    },
  ];

  const structureFormFields = [
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
      name: "package_lpa",
      label: "Package (LPA)",
      type: "number",
    },
    {
      name: "monthly_salary",
      label: "Monthly Salary",
      type: "number",
    },
    {
      name: "pf_percentage",
      label: "PF Percentage",
      type: "number",
    },
    {
      name: "esi_percentage",
      label: "ESI Percentage",
      type: "number",
    },
    {
      name: "allowances",
      label: "Allowances",
      type: "number",
    },
    {
      name: "deductions",
      label: "Deductions",
      type: "number",
    },
  ];

  const handleSubmit = async (formData) => {
    try {
      if (editingStructure) {
        await updateStructure({
          id: editingStructure.id,
          ...formData,
        }).unwrap();
        toast.success("Structure updated successfully");
      } else {
        await createStructure(formData).unwrap();
        toast.success("Structure created successfully");
      }
      refetch();
      setShowForm(false);
      setEditingStructure(null);
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  const handleDelete = async (row) => {
    if (!window.confirm("Are you sure you want to delete this structure?"))
      return;

    try {
      await deleteStructure(row.id).unwrap();
      toast.success("Structure deleted successfully");
      refetch();
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Structures</h1>
        <Button label="Add Structure" onClick={() => setShowForm(true)} />
      </div>

      <DataTable
        loading={isLoading}
        data={data?.data || []}
        columns={columns}
        onEdit={(row) => {
          setEditingStructure(row);
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
          title={editingStructure ? "Edit Structure" : "Create Structure"}
          onClose={() => {
            setShowForm(false);
            setEditingStructure(null);
          }}
        >
          <DynamicForm
            fields={structureFormFields}
            initialValues={editingStructure ? editingStructure : {}}
            onSubmit={handleSubmit}
          />
        </Modal>
      )}
    </div>
  );
};

export default SalaryStructures;
