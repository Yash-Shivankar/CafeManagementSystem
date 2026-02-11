import { useState } from "react";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import { toast } from "react-toastify";

import {
  useGetServicesQuery,
  useCreateServiceMutation,
  useUpdateServiceMutation,
  useDeleteServiceMutation,
} from "../../app/allSlices";

const Services = () => {
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingService, setEditingService] = useState(null);

  const limit = 10;

  const { data, isLoading, refetch } = useGetServicesQuery({ page, limit });

  const [createService] = useCreateServiceMutation();
  const [updateService] = useUpdateServiceMutation();
  const [deleteService] = useDeleteServiceMutation();

  const columns = [
    { key: "id", label: "Id" },
    { key: "name", label: "Service Name" },
    {
      key: "price",
      label: "Price",
      render: (price) =>
        price !== null && price !== undefined
          ? `₹ ${Number(price).toFixed(2)}`
          : "-",
    },
  ];

  const serviceFormFields = [
    { name: "name", label: "Service Name", type: "text" },
    {
      name: "price",
      label: "Service Price",
      type: "number",
      step: "0.01",
      min: 0,
      required: true,
    },
  ];

  const handleSubmit = async (formData) => {
    try {
      if (editingService) {
        await updateService({
          id: editingService.id,
          ...formData,
        }).unwrap();
        toast.success("Service updated successfully");
      } else {
        await createService(formData).unwrap();
        toast.success("Service created successfully");
      }
      refetch();
      setShowForm(false);
      setEditingService(null);
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  const handleDelete = async (row) => {
    if (!window.confirm("Are you sure you want to delete this service?"))
      return;

    try {
      await deleteService(row.id).unwrap();
      toast.success("Service deleted successfully");
      refetch();
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Services</h1>
        <Button label="Add Service" onClick={() => setShowForm(true)} />
      </div>

      <DataTable
        loading={isLoading}
        data={data?.data || []}
        columns={columns}
        onEdit={(row) => {
          setEditingService(row);
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
          title={editingService ? "Edit Service" : "Create Service"}
          onClose={() => {
            setShowForm(false);
            setEditingService(null);
          }}
        >
          <DynamicForm
            fields={serviceFormFields}
            initialValues={editingService ? editingService : {}}
            onSubmit={handleSubmit}
          />
        </Modal>
      )}
    </div>
  );
};

export default Services;
