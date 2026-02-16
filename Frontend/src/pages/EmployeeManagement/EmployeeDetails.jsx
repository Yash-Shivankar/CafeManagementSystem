import { useState } from "react";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import FilterBar from "../../components/FilterBar";
import { toast } from "react-toastify";

import {
  useGetEmployeeDetailsQuery,
  useCreateEmployeeDetailMutation,
  useUpdateEmployeeDetailMutation,
  useDeleteEmployeeDetailMutation,
  useGetUsersQuery,
  useGetDesignationsQuery,
  useGetDepartmentsQuery,
} from "../../app/allSlices";

const EmployeeDetails = () => {
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingDetail, setEditingDetail] = useState(null);
  const [filters, setFilters] = useState({});
  const [appliedFilters, setAppliedFilters] = useState({});

  const limit = 10;

  const { data, isLoading, refetch } = useGetEmployeeDetailsQuery({
    page,
    limit,
    ...appliedFilters,
  });
  const { data: usersData } = useGetUsersQuery();
  const { data: DesignationsData } = useGetDesignationsQuery();
  const { data: DepartmentsData } = useGetDepartmentsQuery();

  const [createDetail] = useCreateEmployeeDetailMutation();
  const [updateDetail] = useUpdateEmployeeDetailMutation();
  const [deleteDetail] = useDeleteEmployeeDetailMutation();

  const userFiltersConfig = [
    {
      name: "search",
      label: "Search",
      type: "text",
      placeholder: "User / Employee Code",
    },
    {
      name: "employment_type",
      label: "Employment Type",
      type: "select",
      options: [
        { label: "Full Time", value: "full-time" },
        { label: "Part Time", value: "part-time" },
        { label: "Contract", value: "contract" },
        { label: "Intern", value: "intern" },
      ],
    },
    {
      name: "department_id",
      label: "Department",
      type: "select",
      options:
        DepartmentsData?.data?.map((dept) => ({
          label: dept.department_name,
          value: dept.id,
        })) || [],
    },
    {
      name: "designation_id",
      label: "Designation",
      type: "select",
      options:
        DesignationsData?.data?.map((desg) => ({
          label: desg.designation_name,
          value: desg.id,
        })) || [],
    },
    {
      name: "status",
      label: "Status",
      type: "select",
      options: [
        { label: "Active", value: "active" },
        { label: "Inactive", value: "inactive" },
        { label: "Resigned", value: "resigned" },
        { label: "Terminated", value: "terminated" },
      ],
    },
  ];

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const applyFilters = () => {
    const cleanedFilters = Object.fromEntries(
      Object.entries(filters).filter(
        ([_, value]) => value !== "" && value !== null && value !== undefined,
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
    {
      key: "user",
      label: "User",
      render: (user) =>
        `${user?.first_name ?? ""} ${user?.last_name ?? ""}`.trim(),
    },
    { key: "employee_code", label: "Employee Code" },
    { key: "employment_type", label: "Employment Type" },
    {
      key: "department",
      label: "Department",
      render: (dept) => dept?.department_name ?? "-",
    },
    {
      key: "designation",
      label: "Designation",
      render: (desg) => desg?.designation_name ?? "-",
    },
    {
      key: "joining_date",
      label: "Joining Date",
      render: (value) => {
        const date = new Date(value);
        return date.toLocaleDateString("en-GB", {
          day: "2-digit",
          month: "short",
          year: "numeric",
        });
      },
    },
    {
      key: "status",
      label: "Status",
      render: (status) =>
        status
          ? status.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())
          : "-",
    },
  ];

  const detailsFormFields = [
    {
      name: "user_id",
      label: "User",
      type: "select",
      options:
        usersData?.data?.map((u) => ({
          label: `${u.first_name} ${u.last_name}`.trim(),
          value: u.id,
        })) || [],
    },
    { name: "employee_code", label: "Employee Code", type: "text" },
    {
      name: "joining_date",
      label: "Joining Date",
      type: "date",
    },
    {
      name: "employment_type",
      label: "Employment Type",
      type: "select",
      options: [
        { label: "Full Time", value: "full-time" },
        { label: "Part Time", value: "part-time" },
        { label: "Contract", value: "contract" },
        { label: "Intern", value: "intern" },
      ],
    },
    {
      name: "status",
      label: "Status",
      type: "select",
      options: [
        { label: "Active", value: "active" },
        { label: "Inactive", value: "inactive" },
        { label: "Resigned", value: "resigned" },
        { label: "Terminated", value: "terminated" },
      ],
    },
    {
      name: "department_id",
      label: "Departments",
      type: "select",
      options:
        DepartmentsData?.data?.map((dept) => ({
          label: dept.department_name,
          value: dept.id,
        })) || [],
    },
    {
      name: "designation_id",
      label: "Designations",
      type: "select",
      options:
        DesignationsData?.data?.map((desg) => ({
          label: desg.designation_name,
          value: desg.id,
        })) || [],
    },
  ];

  const handleSubmit = async (formData) => {
    try {
      if (editingDetail) {
        await updateDetail({
          id: editingDetail.id,
          ...formData,
        }).unwrap();
        toast.success("Employee Details updated successfully");
      } else {
        await createDetail(formData).unwrap();
        toast.success("Employee Details created successfully");
      }
      refetch();
      setShowForm(false);
      setEditingDetail(null);
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  const handleDelete = async (row) => {
    if (
      !window.confirm("Are you sure you want to delete this employee details?")
    )
      return;

    try {
      await deleteDetail(row.id).unwrap();
      toast.success("Employee Details deleted successfully");
      refetch();
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Employee Details</h1>
        <Button
          label="Add Employee Details"
          onClick={() => setShowForm(true)}
        />
      </div>

      <FilterBar
        filters={userFiltersConfig}
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
          setEditingDetail(row);
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
          title={
            editingDetail ? "Edit Employee Details" : "Create Employee Details"
          }
          onClose={() => {
            setShowForm(false);
            setEditingDetail(null);
          }}
        >
          <DynamicForm
            fields={detailsFormFields}
            initialValues={editingDetail ? editingDetail : {}}
            onSubmit={handleSubmit}
          />
        </Modal>
      )}
    </div>
  );
};

export default EmployeeDetails;
