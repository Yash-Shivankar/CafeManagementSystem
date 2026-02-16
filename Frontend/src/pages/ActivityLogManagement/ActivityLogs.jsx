import { useState } from "react";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import { toast } from "react-toastify";

import {
  useGetDepartmentsQuery,
  useCreateDepartmentMutation,
  useUpdateDepartmentMutation,
  useDeleteDepartmentMutation,
} from "../../app/allSlices";

const ActivityLogs = () => {
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingDepartment, setEditingDepartment] = useState(null);

  const limit = 10;

  const { data, isLoading, refetch } = useGetDepartmentsQuery({ page, limit });

  const [createDepartment] = useCreateDepartmentMutation();
  const [updateDepartment] = useUpdateDepartmentMutation();
  const [deleteDepartment] = useDeleteDepartmentMutation();

  const columns = [
    { key: "id", label: "Id" },
    { key: "department_name", label: "Department Name" },
  ];

  const departmentFormFields = [
    { name: "department_name", label: "Department Name", type: "text" },
  ];

  const handleSubmit = async (formData) => {
    try {
      if (editingDepartment) {
        await updateDepartment({
          id: editingDepartment.id,
          ...formData,
        }).unwrap();
        toast.success("Department updated successfully");
      } else {
        await createDepartment(formData).unwrap();
        toast.success("Department created successfully");
      }
      refetch();
      setShowForm(false);
      setEditingDepartment(null);
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  const handleDelete = async (row) => {
    if (!window.confirm("Are you sure you want to delete this department?"))
      return;

    try {
      await deleteDepartment(row.id).unwrap();
      toast.success("Department deleted successfully");
      refetch();
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Departments</h1>
        <Button label="Add Department" onClick={() => setShowForm(true)} />
      </div>

      <DataTable
        loading={isLoading}
        data={data?.data || []}
        columns={columns}
        onEdit={(row) => {
          setEditingDepartment(row);
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
          title={editingDepartment ? "Edit Department" : "Create Department"}
          onClose={() => {
            setShowForm(false);
            setEditingDepartment(null);
          }}
        >
          <DynamicForm
            fields={departmentFormFields}
            initialValues={editingDepartment ? editingDepartment : {}}
            onSubmit={handleSubmit}
          />
        </Modal>
      )}
    </div>
  );
};

export default ActivityLogs;
