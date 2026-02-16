import { useState } from "react";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import { toast } from "react-toastify";

import {
  useGetSalaryPaymentsQuery,
  useCreateSalaryPaymentMutation,
  useUpdateSalaryPaymentMutation,
  useDeleteSalaryPaymentMutation,
  useGetEmployeeDetailsQuery,
} from "../../app/allSlices";

const SalaryPayments = () => {
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingPayment, setEditingPayment] = useState(null);

  const limit = 10;

  const { data, isLoading, refetch } = useGetSalaryPaymentsQuery({
    page,
    limit,
  });
  const { data: detailsData } = useGetEmployeeDetailsQuery();

  const [createPayment] = useCreateSalaryPaymentMutation();
  const [updatePayment] = useUpdateSalaryPaymentMutation();
  const [deletePayment] = useDeleteSalaryPaymentMutation();

  const columns = [
    { key: "id", label: "Id" },
    {
      key: "employee",
      label: "Employee",
      render: (employee) =>
        `${employee?.user?.first_name ?? ""} ${employee?.user?.last_name ?? ""}`.trim(),
    },
    { key: "month", label: "Month" },
    { key: "year", label: "Year" },
    {
      key: "gross_salary",
      label: "Gross Salary (₹)",
      render: (v) => `₹ ${Number(v).toLocaleString("en-IN")}`,
    },
    {
      key: "pf_deducted",
      label: "PF (₹)",
      render: (v) => `₹ ${Number(v).toLocaleString("en-IN")}`,
    },
    {
      key: "esi_deducted",
      label: "ESI (₹)",
      render: (v) => `₹ ${Number(v).toLocaleString("en-IN")}`,
    },
    {
      key: "net_salary",
      label: "Net Salary (₹)",
      render: (v) => `₹ ${Number(v).toLocaleString("en-IN")}`,
    },
    {
      key: "paid_on",
      label: "Paid On",
      render: (v) =>
        v
          ? new Date(v).toLocaleDateString("en-GB", {
              day: "2-digit",
              month: "short",
              year: "numeric",
            })
          : "Unpaid",
    },
  ];

  const paymentFormFields = [
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
      required: true,
    },
    {
      name: "month",
      label: "Month",
      type: "select",
      options: [
        { label: "January", value: "January" },
        { label: "February", value: "February" },
        { label: "March", value: "March" },
        { label: "April", value: "April" },
        { label: "May", value: "May" },
        { label: "June", value: "June" },
        { label: "July", value: "July" },
        { label: "August", value: "August" },
        { label: "September", value: "September" },
        { label: "October", value: "October" },
        { label: "November", value: "November" },
        { label: "December", value: "December" },
      ],
      required: true,
    },
    {
      name: "year",
      label: "Year",
      type: "number",
      min: 2000,
      max: 2100,
      required: true,
    },
    {
      name: "gross_salary",
      label: "Gross Salary (₹)",
      type: "number",
      step: "0.01",
      required: true,
    },
    {
      name: "pf_deducted",
      label: "PF Deduction (₹)",
      type: "number",
      step: "0.01",
    },
    {
      name: "esi_deducted",
      label: "ESI Deduction (₹)",
      type: "number",
      step: "0.01",
    },
    {
      name: "paid_on",
      label: "Paid On",
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
                    paid_on: editingPayment.paid_on
                      ? editingPayment.paid_on.split("T")[0]
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

export default SalaryPayments;
