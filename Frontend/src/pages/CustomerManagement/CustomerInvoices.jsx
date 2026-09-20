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
  useGetCustomerInvoicesQuery,
  useCreateCustomerInvoiceMutation,
  useUpdateCustomerInvoiceMutation,
  useDeleteCustomerInvoiceMutation,
  useGetUsersQuery,
} from "../../app/allSlices";

const CustomerInvoices = () => {
  const confirm = useConfirm();
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingInvoice, setEditingInvoice] = useState(null);
  const [filters, setFilters] = useState({});
  const [appliedFilters, setAppliedFilters] = useState({});

  const limit = 10;

  const { data, isLoading, refetch } = useGetCustomerInvoicesQuery({
    page,
    limit,
    ...appliedFilters,
  });

  const { data: usersData } = useGetUsersQuery();
  const [createInvoice] = useCreateCustomerInvoiceMutation();
  const [updateInvoice] = useUpdateCustomerInvoiceMutation();
  const [deleteInvoice] = useDeleteCustomerInvoiceMutation();

  const today = new Date().toISOString().split("T")[0];

  const invoiceFiltersConfig = [
    {
      name: "search",
      label: "Search",
      type: "text",
      placeholder: "User",
    },
    {
      name: "status",
      label: "Status",
      type: "select",
      options: [
        { label: "Paid", value: "paid" },
        { label: "Unpaid", value: "unpaid" },
        { label: "Partial", value: "partial" },
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
      key: "user",
      label: "User",
      render: (user) =>
        `${user?.first_name ?? ""} ${user?.last_name ?? ""}`.trim(),
    },
    {
      key: "total_amount",
      label: "Total Amount",
      render: (value) => formatMoney(value),
    },
    {
      key: "paid_amount",
      label: "Paid Amount",
      render: (value) => formatMoney(value),
    },
    { key: "status", label: "Status" },
    {
      key: "invoice_date",
      label: "Invoice Date",
      render: (value) => formatDate(value),
    },
  ];

  const invoiceFormFields = [
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
      name: "total_amount",
      label: "Total Amount",
      type: "number",
      min: 0.01,
      step: "0.01",
      required: true,
    },
    {
      name: "paid_amount",
      label: "Paid Amount",
      type: "number",
      min: 0.01,
      step: "0.01",
      required: true,
    },
    {
      name: "status",
      label: "Status",
      type: "select",
      options: [
        { label: "Paid", value: "paid" },
        { label: "Unpaid", value: "unpaid" },
        { label: "Partial", value: "partial" },
      ],
    },
  ];

  const handleSubmit = async (formData) => {
    try {
      if (editingInvoice) {
        await updateInvoice({
          id: editingInvoice.id,
          ...formData,
        }).unwrap();
        toast.success("Invoice updated successfully");
      } else {
        await createInvoice({ ...formData, invoice_date: today }).unwrap();
        toast.success("Invoice created successfully");
      }
      refetch();
      setShowForm(false);
      setEditingInvoice(null);
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  const handleDelete = async (row) => {
    if (!(await confirm({
          title: "Delete this invoice?",
          message:
            "It will stop appearing in lists and reports. This cannot be undone from the app.",
          tone: "danger",
          confirmLabel: "Delete",
          }))) {
      return;
    }try {
      await deleteInvoice(row.id).unwrap();
      toast.success("Invoice deleted successfully");
      refetch();
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Invoices</h1>
        <Button label="Add Invoice" onClick={() => setShowForm(true)} />
      </div>

      <FilterBar
        filters={invoiceFiltersConfig}
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
          setEditingInvoice(row);
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
          title={editingInvoice ? "Edit Invoice" : "Create Invoice"}
          onClose={() => {
            setShowForm(false);
            setEditingInvoice(null);
          }}
        >
          <DynamicForm
            fields={invoiceFormFields}
            initialValues={
              editingInvoice
                ? {
                    ...editingInvoice,
                    user_id: editingInvoice.user?.id,
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

export default CustomerInvoices;
