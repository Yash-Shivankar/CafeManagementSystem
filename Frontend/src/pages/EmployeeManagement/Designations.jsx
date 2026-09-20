import { useState } from "react";
import { useConfirm } from "../../components/useConfirm";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import FilterBar from "../../components/FilterBar";
import { toast } from "react-toastify";

import {
  useGetDesignationsQuery,
  useCreateDesignationMutation,
  useUpdateDesignationMutation,
  useDeleteDesignationMutation,
} from "../../app/allSlices";

const Designations = () => {
  const confirm = useConfirm();
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingDesignation, setEditingDesignation] = useState(null);
  const [filters, setFilters] = useState({});
  const [appliedFilters, setAppliedFilters] = useState({});

  const limit = 10;

  const { data, isLoading, refetch } = useGetDesignationsQuery({
    page,
    limit,
    ...appliedFilters,
  });

  const [createDesignation] = useCreateDesignationMutation();
  const [updateDesignation] = useUpdateDesignationMutation();
  const [deleteDesignation] = useDeleteDesignationMutation();

  const designationFiltersConfig = [
    {
      name: "search",
      label: "Search",
      type: "text",
      placeholder: "Designation Name",
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
    { key: "designation_name", label: "Designation Name" },
  ];

  const designationFormFields = [
    { name: "designation_name", label: "Designation Name", type: "text" },
  ];

  const handleSubmit = async (formData) => {
    try {
      if (editingDesignation) {
        await updateDesignation({
          id: editingDesignation.id,
          ...formData,
        }).unwrap();
        toast.success("Designation updated successfully");
      } else {
        await createDesignation(formData).unwrap();
        toast.success("Designation created successfully");
      }
      refetch();
      setShowForm(false);
      setEditingDesignation(null);
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  const handleDelete = async (row) => {
    if (!(await confirm({
        title: "Delete this designation?",
        message:
          "It will stop appearing in lists and reports. This cannot be undone from the app.",
        tone: "danger",
        confirmLabel: "Delete",
        }))) {
      return;
    }try {
      await deleteDesignation(row.id).unwrap();
      toast.success("Designation deleted successfully");
      refetch();
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Designations</h1>
        <Button label="Add Designation" onClick={() => setShowForm(true)} />
      </div>

      <FilterBar
        filters={designationFiltersConfig}
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
          setEditingDesignation(row);
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
          title={editingDesignation ? "Edit Designation" : "Create Designation"}
          onClose={() => {
            setShowForm(false);
            setEditingDesignation(null);
          }}
        >
          <DynamicForm
            fields={designationFormFields}
            initialValues={editingDesignation ? editingDesignation : {}}
            onSubmit={handleSubmit}
          />
        </Modal>
      )}
    </div>
  );
};

export default Designations;
