import { useState } from "react";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import { toast } from "react-toastify";

import {
  useGetRolesQuery,
  useCreateRoleMutation,
  useUpdateRoleMutation,
  useDeleteRoleMutation,
} from "../../app/allSlices";

const Roles = () => {
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingRole, setEditingRole] = useState(null);

  const limit = 10;

  const { data, isLoading, refetch } = useGetRolesQuery({ page, limit });

  const [createRole] = useCreateRoleMutation();
  const [updateRole] = useUpdateRoleMutation();
  const [deleteRole] = useDeleteRoleMutation();

  const columns = [
    { key: "id", label: "Id" },
    { key: "role_name", label: "Role Name" },
  ];

  const roleFormFields = [
    { name: "role_name", label: "Role Name", type: "text" },
  ];

  const handleSubmit = async (formData) => {
    try {
      if (editingRole) {
        await updateRole({ id: editingRole.id, ...formData }).unwrap();
        toast.success("Role updated successfully");
      } else {
        await createRole(formData).unwrap();
        toast.success("Role created successfully");
      }
      refetch();
      setShowForm(false);
      setEditingRole(null);
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  const handleDelete = async (row) => {
    if (!window.confirm("Are you sure you want to delete this role?")) return;

    try {
      await deleteRole(row.id).unwrap();
      toast.success("Role deleted successfully");
      refetch();
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Roles</h1>
        <Button label="Add Role" onClick={() => setShowForm(true)} />
      </div>

      <DataTable
        loading={isLoading}
        data={data?.data || []}
        columns={columns}
        onEdit={(row) => {
          setEditingRole(row);
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
          title={editingRole ? "Edit Role" : "Create Role"}
          onClose={() => {
            setShowForm(false);
            setEditingRole(null);
          }}
        >
          <DynamicForm
            fields={roleFormFields}
            initialValues={editingRole ? editingRole : {}}
            onSubmit={handleSubmit}
          />
        </Modal>
      )}
    </div>
  );
};

export default Roles;
