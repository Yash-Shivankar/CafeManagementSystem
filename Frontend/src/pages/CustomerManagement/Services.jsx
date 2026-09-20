import { useState } from "react";
import { formatMoney } from "../../utils/format";
import { useConfirm } from "../../components/useConfirm";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import FilterBar from "../../components/FilterBar";
import { toast } from "react-toastify";

import {
  useGetServicesQuery,
  useCreateServiceMutation,
  useUpdateServiceMutation,
  useDeleteServiceMutation,
} from "../../app/allSlices";

const Services = () => {
  const confirm = useConfirm();
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingService, setEditingService] = useState(null);
  const [filters, setFilters] = useState({});
  const [appliedFilters, setAppliedFilters] = useState({});

  const limit = 10;

  const { data, isLoading, refetch } = useGetServicesQuery({
    page,
    limit,
    ...appliedFilters,
  });

  const [createService] = useCreateServiceMutation();
  const [updateService] = useUpdateServiceMutation();
  const [deleteService] = useDeleteServiceMutation();

  const serviceFiltersConfig = [
    {
      name: "search",
      label: "Search",
      type: "text",
      placeholder: "Service Name / Price",
    },
  ];

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const applyFilters = () => {
    const cleanedFilters = Object.fromEntries(
      Object.entries(filters).filter(
        ([, value]) => value !== "" && value !== null && value !== undefined,
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
    { key: "name", label: "Service Name" },
    {
      key: "price",
      label: "Price",
      render: (price) =>
        price !== null && price !== undefined
          ? formatMoney(price)
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
    if (!(await confirm({
          title: "Delete this service?",
          message:
            "It will stop appearing in lists and reports. This cannot be undone from the app.",
          tone: "danger",
          confirmLabel: "Delete",
          }))) {
      return;
    }try {
      await deleteService(row.id).unwrap();
      toast.success("Service deleted successfully");
      refetch();
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Services</h1>
        <Button label="Add Service" onClick={() => setShowForm(true)} />
      </div>

      <FilterBar
        filters={serviceFiltersConfig}
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
