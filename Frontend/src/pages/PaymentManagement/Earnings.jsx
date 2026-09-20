import { useState } from "react";
import { formatDate, formatMoney } from "../../utils/format";
import { useConfirm } from "../../components/useConfirm";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import FilterBar from "../../components/FilterBar";
import { toast } from "react-toastify";

import {
  useGetEarningsQuery,
  useCreateEarningMutation,
  useUpdateEarningMutation,
  useDeleteEarningMutation,
} from "../../app/allSlices";

const Earnings = () => {
  const confirm = useConfirm();
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingEarning, setEditingEarning] = useState(null);
  const [filters, setFilters] = useState({});
  const [appliedFilters, setAppliedFilters] = useState({});

  const limit = 10;

  const { data, isLoading, refetch } = useGetEarningsQuery({
    page,
    limit,
    ...appliedFilters,
  });

  const [createEarning] = useCreateEarningMutation();
  const [updateEarning] = useUpdateEarningMutation();
  const [deleteEarning] = useDeleteEarningMutation();

  const earningFiltersConfig = [
    {
      name: "start_date",
      label: "Start Date",
      type: "date",
    },
    {
      name: "end_date",
      label: "End Date",
      type: "date",
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
    {
      key: "date",
      label: "Date",
      render: (value) => formatDate(value),
    },
    {
      key: "revenue",
      label: "Revenue",
      render: (v) => formatMoney(v),
    },
    {
      key: "expenses",
      label: "Expenses",
      render: (v) => formatMoney(v),
    },
    {
      key: "profit",
      label: "Profit / Loss",
      render: (v) => (
        <span
          className={
            v < 0
              ? "text-red-600 font-semibold"
              : "text-green-600 font-semibold"
          }
        >
          ₹ {Number(v).toFixed(2)}
        </span>
      ),
    },
  ];

  const earningFormFields = [
    {
      name: "date",
      label: "Date",
      type: "date",
      required: true,
    },
    {
      name: "revenue",
      label: "Revenue",
      type: "number",
      min: 0,
      step: "0.01",
      required: true,
    },
    {
      name: "expenses",
      label: "Expenses",
      type: "number",
      min: 0,
      step: "0.01",
      required: true,
    },
  ];

  const handleSubmit = async (formData) => {
    try {
      if (editingEarning) {
        await updateEarning({
          id: editingEarning.id,
          ...formData,
        }).unwrap();
        toast.success("Earning updated successfully");
      } else {
        await createEarning(formData).unwrap();
        toast.success("Earning created successfully");
      }
      refetch();
      setShowForm(false);
      setEditingEarning(null);
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  const handleDelete = async (row) => {
    if (!(await confirm({
        title: "Delete this earning?",
        message:
          "It will stop appearing in lists and reports. This cannot be undone from the app.",
        tone: "danger",
        confirmLabel: "Delete",
        }))) {
      return;
    }try {
      await deleteEarning(row.id).unwrap();
      toast.success("Earning deleted successfully");
      refetch();
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Earnings</h1>
        <Button label="Add Earning" onClick={() => setShowForm(true)} />
      </div>

      <FilterBar
        filters={earningFiltersConfig}
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
          setEditingEarning(row);
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
          title={editingEarning ? "Edit Earning" : "Create Earning"}
          onClose={() => {
            setShowForm(false);
            setEditingEarning(null);
          }}
        >
          <DynamicForm
            fields={earningFormFields}
            initialValues={editingEarning ? editingEarning : {}}
            onSubmit={handleSubmit}
          />
        </Modal>
      )}
    </div>
  );
};

export default Earnings;
