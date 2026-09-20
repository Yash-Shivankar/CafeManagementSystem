import { useState } from "react";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import FilterBar from "../../components/FilterBar";
import { toast } from "react-toastify";
import { usePermissions } from "../../services/usePermissions";

import {
  useGetOutletsQuery,
  useCreateOutletMutation,
  useUpdateOutletMutation,
} from "../../app/allSlices";

const Outlets = () => {
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingOutlet, setEditingOutlet] = useState(null);
  const [filters, setFilters] = useState({});
  const [appliedFilters, setAppliedFilters] = useState({});

  const { canCreate, canUpdate } = usePermissions();

  const limit = 10;

  const { data, isLoading, refetch } = useGetOutletsQuery({
    page,
    limit,
    ...appliedFilters,
  });

  const [createOutlet] = useCreateOutletMutation();
  const [updateOutlet] = useUpdateOutletMutation();

  const outletFiltersConfig = [
    {
      name: "search",
      label: "Search",
      type: "text",
      placeholder: "Name, code, city or GSTIN",
    },
    {
      name: "is_active",
      label: "Status",
      type: "select",
      options: [
        { value: "true", label: "Active" },
        { value: "false", label: "Retired" },
      ],
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
    { key: "code", label: "Code" },
    { key: "name", label: "Outlet Name" },
    { key: "city", label: "City" },
    { key: "gstin", label: "GSTIN" },
    {
      key: "is_active",
      label: "Status",
      render: (value) => (value ? "Active" : "Retired"),
    },
  ];

  const outletFormFields = [
    { name: "name", label: "Outlet Name", type: "text" },
    { name: "code", label: "Code (e.g. MAIN, KOR)", type: "text" },
    { name: "address_line1", label: "Address line 1", type: "text" },
    { name: "address_line2", label: "Address line 2", type: "text" },
    { name: "city", label: "City", type: "text" },
    { name: "state", label: "State", type: "text" },
    { name: "pincode", label: "Pincode", type: "text" },
    { name: "phone", label: "Phone", type: "text" },
    { name: "email", label: "Email", type: "text" },
    { name: "gstin", label: "GSTIN (15 characters)", type: "text" },
    { name: "fssai_license", label: "FSSAI licence (14 digits)", type: "text" },
    {
      name: "is_active",
      label: "Status",
      type: "select",
      options: [
        { value: "true", label: "Active" },
        { value: "false", label: "Retired" },
      ],
    },
  ];

  const handleSubmit = async (formData) => {
    const payload = Object.fromEntries(
      Object.entries(formData).filter(([, value]) => value !== ""),
    );
    if (payload.is_active !== undefined) {
      payload.is_active = payload.is_active === "true" || payload.is_active === true;
    }

    try {
      if (editingOutlet) {
        await updateOutlet({ id: editingOutlet.id, ...payload }).unwrap();
        toast.success("Outlet updated successfully");
      } else {
        await createOutlet(payload).unwrap();
        toast.success("Outlet created successfully");
      }
      refetch();
      setShowForm(false);
      setEditingOutlet(null);
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(
        typeof errorMsg === "string" ? errorMsg : "Please check the form fields",
      );
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Outlets</h1>
        {canCreate("outlets") && (
          <Button label="Add Outlet" onClick={() => setShowForm(true)} />
        )}
      </div>

      <FilterBar
        filters={outletFiltersConfig}
        values={filters}
        onChange={handleFilterChange}
        onApply={applyFilters}
        onReset={resetFilters}
      />

      <DataTable
        loading={isLoading}
        data={data?.data || []}
        columns={columns}
        onEdit={
          canUpdate("outlets")
            ? (row) => {
                setEditingOutlet(row);
                setShowForm(true);
              }
            : undefined
        }

        pagination={{
          currentPage: data?.currentPage || page,
          totalPages: data?.totalPages || 1,
        }}
        onPageChange={setPage}
      />

      {showForm && (
        <Modal
          title={editingOutlet ? "Edit Outlet" : "Create Outlet"}
          onClose={() => {
            setShowForm(false);
            setEditingOutlet(null);
          }}
        >
          <DynamicForm
            fields={outletFormFields}
            initialValues={
              editingOutlet
                ? { ...editingOutlet, is_active: String(editingOutlet.is_active) }
                : { is_active: "true" }
            }
            onSubmit={handleSubmit}
          />
        </Modal>
      )}
    </div>
  );
};

export default Outlets;
