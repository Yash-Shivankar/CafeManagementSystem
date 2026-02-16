import { useState } from "react";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import { toast } from "react-toastify";
import StarDisplay from "../../components/StarDisplay";

import {
  useGetEmployeePerformancesQuery,
  useCreateEmployeePerformanceMutation,
  useUpdateEmployeePerformanceMutation,
  useDeleteEmployeePerformanceMutation,
  useGetEmployeeDetailsQuery,
} from "../../app/allSlices";

const EmployeePerformances = () => {
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingPerformance, setEditingPerformance] = useState(null);

  const limit = 10;

  const { data, isLoading, refetch } = useGetEmployeePerformancesQuery({
    page,
    limit,
  });
  const { data: detailsData } = useGetEmployeeDetailsQuery();

  const [createPerformance] = useCreateEmployeePerformanceMutation();
  const [updatePerformance] = useUpdateEmployeePerformanceMutation();
  const [deletePerformance] = useDeleteEmployeePerformanceMutation();

  const columns = [
    { key: "id", label: "Id" },
    {
      key: "employee",
      label: "Employee Name",
      render: (employee) =>
        `${employee?.user?.first_name ?? ""} ${employee?.user?.last_name ?? ""}`.trim(),
    },
    {
      key: "rating",
      label: "Rating",
      render: (rating) => <StarDisplay value={rating} />,
    },
    { key: "feedback", label: "Feedback" },
    {
      key: "review_date",
      label: "Review Date",
      render: (value) => {
        const date = new Date(value);
        return date.toLocaleDateString("en-GB", {
          day: "2-digit",
          month: "short",
          year: "numeric",
        });
      },
    },
  ];

  const performancesFormFields = [
    {
      name: "employee_id",
      label: "Employee",
      type: "select",
      options:
        detailsData?.data?.map((u) => ({
          label:
            `${u?.user?.first_name || ""} ${u?.user?.last_name || ""}`.trim(),
          value: u.id,
        })) || [],
    },
    {
      name: "rating",
      label: "Rating",
      type: "stars",
      max: 5,
      required: true,
    },
    { name: "feedback", label: "Feedback", type: "text" },
    {
      name: "review_date",
      label: "Review Date",
      type: "date",
    },
  ];

  const handleSubmit = async (formData) => {
    try {
      if (editingPerformance) {
        await updatePerformance({
          ...formData,
          id: editingPerformance.id,
        }).unwrap();
        toast.success("Employee Performances updated successfully");
      } else {
        await createPerformance(formData).unwrap();
        toast.success("Employee Performances created successfully");
      }
      refetch();
      setShowForm(false);
      setEditingPerformance(null);
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  const handleDelete = async (row) => {
    if (
      !window.confirm(
        "Are you sure you want to delete this employee performances?",
      )
    )
      return;

    try {
      await deletePerformance(row.id).unwrap();
      toast.success("Employee Performances deleted successfully");
      refetch();
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Employee Performances</h1>
        <Button
          label="Add Employee Performances"
          onClick={() => setShowForm(true)}
        />
      </div>

      <DataTable
        loading={isLoading}
        data={data?.data || []}
        columns={columns}
        onEdit={(row) => {
          setEditingPerformance(row);
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
            editingPerformance
              ? "Edit Employee Performances"
              : "Create Employee Performances"
          }
          onClose={() => {
            setShowForm(false);
            setEditingPerformance(null);
          }}
        >
          <DynamicForm
            fields={performancesFormFields}
            initialValues={
              editingPerformance
                ? {
                    ...editingPerformance,
                    employee_id: editingPerformance.employee?.id,
                    review_date: editingPerformance.review_date
                      ? editingPerformance.review_date.split("T")[0]
                      : "",
                  }
                : {}
            }
            onSubmit={handleSubmit}
          />
        </Modal>
      )}
    </div>
  );
};

export default EmployeePerformances;
