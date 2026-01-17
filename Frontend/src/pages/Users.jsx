import { useState } from "react";
import DataTable from "../components/DataTable";
import { useGetUsersQuery } from "../app/allSlices";

const Users = () => {
  const [page, setPage] = useState(1);
  const limit = 10;

  const { data, isLoading, refetch } = useGetUsersQuery({
    page,
    limit,
    search: "",
  });

  const columns = [
    { key: "first_name", label: "First Name" },
    { key: "last_name", label: "Last Name" },
    { key: "email", label: "Email" },
    { key: "mobile_number", label: "Mobile Number" },
    { key: "role_id", label: "Role" },
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

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Users</h1>

      <DataTable
        data={data?.data || []}
        columns={columns}
        onEdit={(row) => console.log(row)}
        pagination={{
          currentPage: data?.currentPage || page,
          totalPages: data?.totalPages || 1,
        }}
        onPageChange={(newPage) => setPage(newPage)}
      />
    </div>
  );
};

export default Users;
