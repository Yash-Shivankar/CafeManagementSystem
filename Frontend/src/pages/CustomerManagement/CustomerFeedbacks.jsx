import { useState } from "react";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import { toast } from "react-toastify";
import StarDisplay from "../../components/StarDisplay";

import {
  useGetCustomerFeedbacksQuery,
  useCreateCustomerFeedbackMutation,
  useUpdateCustomerFeedbackMutation,
  useDeleteCustomerFeedbackMutation,
  useGetUsersQuery,
} from "../../app/allSlices";

const CustomerFeedbacks = () => {
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingFeedback, setEditingFeedback] = useState(null);

  const limit = 10;

  const { data, isLoading, refetch } = useGetCustomerFeedbacksQuery({
    page,
    limit,
  });

  const { data: usersData } = useGetUsersQuery();
  const [createFeedback] = useCreateCustomerFeedbackMutation();
  const [updateFeedback] = useUpdateCustomerFeedbackMutation();
  const [deleteFeedback] = useDeleteCustomerFeedbackMutation();

  const today = new Date().toISOString().split("T")[0];
  const columns = [
    { key: "id", label: "Id" },
    {
      key: "user",
      label: "User",
      render: (user) =>
        `${user?.first_name ?? ""} ${user?.last_name ?? ""}`.trim(),
    },
    {
      key: "rating",
      label: "Rating",
      render: (rating) => <StarDisplay value={rating} />,
    },
    { key: "feedback", label: "Feedback" },
    {
      key: "date_given",
      label: "Date",
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

  const feedbackFormFields = [
    {
      name: "user_id",
      label: "User",
      type: "select",
      options:
        usersData?.data?.map((u) => ({
          label: `${u?.first_name || ""} ${u?.last_name || ""}`.trim(),
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
  ];

  const handleSubmit = async (formData) => {
    try {
      if (editingFeedback) {
        await updateFeedback({
          id: editingFeedback.id,
          ...formData,
          date_given: editingFeedback.date_given || today,
        }).unwrap();
        toast.success("Feedback updated successfully");
      } else {
        await createFeedback({
          ...formData,
          date_given: today,
        }).unwrap();
        toast.success("Feedback created successfully");
      }
      refetch();
      setShowForm(false);
      setEditingFeedback(null);
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  const handleDelete = async (row) => {
    if (!window.confirm("Are you sure you want to delete this feedback?"))
      return;

    try {
      await deleteFeedback(row.id).unwrap();
      toast.success("Feedback deleted successfully");
      refetch();
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Feedbacks</h1>
        <Button label="Add Feedback" onClick={() => setShowForm(true)} />
      </div>

      <DataTable
        loading={isLoading}
        data={data?.data || []}
        columns={columns}
        onEdit={(row) => {
          setEditingFeedback(row);
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
          title={editingFeedback ? "Edit Feedback" : "Create Feedbackt"}
          onClose={() => {
            setShowForm(false);
            setEditingFeedback(null);
          }}
        >
          <DynamicForm
            fields={feedbackFormFields}
            initialValues={
              editingFeedback
                ? {
                    ...editingFeedback,
                    user_id: editingFeedback.user?.id,
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

export default CustomerFeedbacks;
