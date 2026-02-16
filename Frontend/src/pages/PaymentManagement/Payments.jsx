import { useState } from "react";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import { toast } from "react-toastify";

import {
  useGetPaymentsQuery,
  useCreatePaymentMutation,
  useUpdatePaymentMutation,
  useDeletePaymentMutation,
  useGetCustomerInvoicesQuery,
} from "../../app/allSlices";

const Payments = () => {
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingPayment, setEditingPayment] = useState(null);

  const limit = 10;

  const { data, isLoading, refetch } = useGetPaymentsQuery({ page, limit });

  const { data: invoicesData } = useGetCustomerInvoicesQuery();

  const [createPayment] = useCreatePaymentMutation();
  const [updatePayment] = useUpdatePaymentMutation();
  const [deletePayment] = useDeletePaymentMutation();

  const formatDateForInput = (value) => {
    if (!value) return "";
    return value.split("T")[0];
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
      render: (value) => `₹ ${Number(value).toFixed(2)}`,
    },
    { key: "method", label: "Method" },
    {
      key: "payment_date",
      label: "Payment Date",
      render: (value) =>
        value
          ? new Date(value).toLocaleDateString("en-GB", {
              day: "2-digit",
              month: "short",
              year: "numeric",
            })
          : "-",
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
    if (!window.confirm("Are you sure you want to delete this payment?"))
      return;

    try {
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
