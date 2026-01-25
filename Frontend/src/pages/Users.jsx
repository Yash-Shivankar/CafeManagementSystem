import { useState } from "react";
import DataTable from "../components/DataTable";
import DynamicForm from "../components/DynamicForm";
import Modal from "../components/Modal";
import Button from "../components/Button";
import { toast } from "react-toastify";

import {
  useGetUsersQuery,
  useCreateUserMutation,
  useUpdateUserMutation,
  useDeleteUserMutation,
  useGetRolesQuery,
} from "../app/allSlices";

const Users = () => {
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingUser, setEditingUser] = useState(null);

  const limit = 10;

  const { data, isLoading, refetch } = useGetUsersQuery({ page, limit });
  const { data: rolesData } = useGetRolesQuery();

  const [createUser] = useCreateUserMutation();
  const [updateUser] = useUpdateUserMutation();
  const [deleteUser] = useDeleteUserMutation();

  /* -------------------- COLUMNS (UNCHANGED) -------------------- */

  const columns = [
    { key: "id", label: "Id" },
    { key: "first_name", label: "First Name" },
    { key: "last_name", label: "Last Name" },
    { key: "email", label: "Email" },
    { key: "mobile_number", label: "Mobile Number" },
    {
      key: "role",
      label: "Role",
      render: (v) => v?.role_name ?? "-",
    },
    {
      key: "date_of_birth",
      label: "DOB",
      render: (value) => {
        const date = new Date(value);
        return date.toLocaleDateString("en-GB", {
          day: "2-digit",
          month: "short",
          year: "numeric",
        });
      },
    },
    { key: "gender", label: "Gender" },
    {
      key: "is_active",
      label: "Status",
      render: (v) => (v ? "Active" : "Inactive"),
    },
  ];

  /* -------------------- FORM FIELDS -------------------- */

  const userFormFields = [
    { name: "first_name", label: "First Name", type: "text" },
    { name: "last_name", label: "Last Name", type: "text" },
    { name: "email", label: "Email", type: "email" },
    { name: "mobile_number", label: "Mobile Number", type: "text" },
    { name: "date_of_birth", label: "Date of Birth", type: "date" },
    {
      name: "gender",
      label: "Gender",
      type: "select",
      options: [
        { label: "Male", value: "Male" },
        { label: "Female", value: "Female" },
        { label: "Other", value: "Other" },
      ],
    },
    {
      name: "role_id",
      label: "Role",
      type: "select",
      options:
        rolesData?.data?.map((r) => ({
          label: r.role_name,
          value: r.id,
        })) || [],
    },
    {
      name: "is_active",
      label: "Status",
      type: "select",
      options: [
        { label: "Active", value: true },
        { label: "Inactive", value: false },
      ],
    },
  ];

  /* -------------------- HANDLERS -------------------- */

  const handleSubmit = async (formData) => {
    try {
      if (editingUser) {
        await updateUser({ id: editingUser.id, ...formData }).unwrap();
        toast.success("User updated successfully");
      } else {
        await createUser(formData).unwrap();
        toast.success("User created successfully");
      }
      refetch();
      setShowForm(false);
      setEditingUser(null);
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  const handleDelete = async (row) => {
    if (!window.confirm("Are you sure you want to delete this user?")) return;

    try {
      await deleteUser(row.id).unwrap();
      toast.success("User deleted successfully");
      refetch();
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Users</h1>
        <Button label="Add User" onClick={() => setShowForm(true)} />
      </div>

      <DataTable
        loading={isLoading}
        data={data?.data || []}
        columns={columns}
        onEdit={(row) => {
          setEditingUser(row);
          setShowForm(true);
        }}
        onDelete={handleDelete}
        pagination={{
          currentPage: data?.currentPage || page,
          totalPages: data?.totalPages || 1,
        }}
        onPageChange={setPage}
      />

      {/* -------------------- MODAL -------------------- */}
      {showForm && (
        <Modal
          title={editingUser ? "Edit User" : "Create User"}
          onClose={() => {
            setShowForm(false);
            setEditingUser(null);
          }}
        >
          <DynamicForm
            fields={userFormFields}
            initialValues={
              editingUser
                ? { ...editingUser, role_id: editingUser.role?.id }
                : {}
            }
            onSubmit={handleSubmit}
          />
        </Modal>
      )}
    </div>
  );
};

export default Users;
