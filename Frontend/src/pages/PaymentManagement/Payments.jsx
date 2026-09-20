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
  useGetPaymentsQuery,
  useCreatePaymentMutation,
  useUpdatePaymentMutation,
  useDeletePaymentMutation,
  useGetCustomerInvoicesQuery,
} from "../../app/allSlices";

const Payments = () => {
  const confirm = useConfirm();
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingPayment, setEditingPayment] = useState(null);
  const [filters, setFilters] = useState({});
  const [appliedFilters, setAppliedFilters] = useState({});

  const limit = 10;

  const { data, isLoading, refetch } = useGetPaymentsQuery({
    page,
    limit,
    ...appliedFilters,
  });

  const { data: invoicesData } = useGetCustomerInvoicesQuery();

  const [createPayment] = useCreatePaymentMutation();
  const [updatePayment] = useUpdatePaymentMutation();
  const [deletePayment] = useDeletePaymentMutation();

  const formatDateForInput = (value) => {
    if (!value) return "";
    return value.split("T")[0];
  };

  const paymentFiltersConfig = [
    {
      name: "search",
      label: "Search",
      type: "text",
      placeholder: "Invoice",
    },
    {
      name: "method",
      label: "Payment Method",
      type: "select",
      options: [
        { label: "Cash", value: "cash" },
        { label: "Card", value: "card" },
        { label: "UPI", value: "upi" },
      ],
    },
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
      key: "invoice",
      label: "Invoice",
      render: (invoice) => (invoice ? `#${invoice.id}` : "-"),
    },
    {
      key: "amount",
      label: "Amount",
      render: (value) => formatMoney(value),
    },
    { key: "method", label: "Method" },
    {
      key: "payment_date",
      label: "Payment Date",
      render: (value) => (value ? formatDate(value) : "-"),
    },
  ];

  const paymentFormFields = [
    {
      name: "invoice_id",
      label: "Invoice",
      type: "select",
      options:
        invoicesData?.data?.map((inv) => ({
          label: `Invoice #${inv.id}`,
          value: inv.id,
        })) || [],
      required: true,
    },
    {
      name: "amount",
      label: "Amount",
      type: "number",
      min: 0.01,
      step: "0.01",
      required: true,
    },
    {
      name: "method",
      label: "Payment Method",
      type: "select",
      options: [
        { label: "Cash", value: "cash" },
        { label: "Card", value: "card" },
        { label: "UPI", value: "upi" },
      ],
      required: true,
    },
    {
      name: "payment_date",
      label: "Payment Date",
      type: "date",
    },
  ];

  const handleSubmit = async (formData) => {
    try {
      if (editingPayment) {
        await updatePayment({
          id: editingPayment.id,
          ...formData,
        }).unwrap();
        toast.success("Payment updated successfully");
      } else {
        await createPayment(formData).unwrap();
        toast.success("Payment created successfully");
      }
      refetch();
      setShowForm(false);
      setEditingPayment(null);
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  const handleDelete = async (row) => {
    if (!(await confirm({
        title: "Delete this payment?",
        message:
          "It will stop appearing in lists and reports. This cannot be undone from the app.",
        tone: "danger",
        confirmLabel: "Delete",
        }))) {
      return;
    }try {
      await deletePayment(row.id).unwrap();
      toast.success("Payment deleted successfully");
      refetch();
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Payments</h1>
        <Button label="Add Payment" onClick={() => setShowForm(true)} />
      </div>

      <FilterBar
        filters={paymentFiltersConfig}
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
          setEditingPayment(row);
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
          title={editingPayment ? "Edit Payment" : "Create Payment"}
          onClose={() => {
            setShowForm(false);
            setEditingPayment(null);
          }}
        >
          <DynamicForm
            fields={paymentFormFields}
            initialValues={
              editingPayment
                ? {
                    ...editingPayment,
                    invoice_id: editingPayment.invoice?.id,
                    payment_date: formatDateForInput(
                      editingPayment.payment_date,
                    ),
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

export default Payments;
