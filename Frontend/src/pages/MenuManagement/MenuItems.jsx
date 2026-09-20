import { useState } from "react";
import { toast } from "react-toastify";

import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import FilterBar from "../../components/FilterBar";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import { useConfirm } from "../../components/useConfirm";
import { usePermissions } from "../../services/usePermissions";
import { formatMoney, formatPercent } from "../../utils/format";
import {
  useCreateMenuItemMutation,
  useDeleteMenuItemMutation,
  useGetMenuCategoriesQuery,
  useGetMenuItemsQuery,
  useUpdateMenuItemMutation,
} from "../../app/allSlices";

const GST_RATES = [
  { value: "0", label: "0% — exempt" },
  { value: "5", label: "5% — food served" },
  { value: "12", label: "12%" },
  { value: "18", label: "18% — sealed / packaged" },
  { value: "28", label: "28%" },
];

const MenuItems = () => {
  const confirm = useConfirm();
  const { canCreate, canUpdate, canDelete } = usePermissions();

  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [filters, setFilters] = useState({});
  const [appliedFilters, setAppliedFilters] = useState({});

  const limit = 10;
  const { data, isFetching } = useGetMenuItemsQuery({ page, limit, ...appliedFilters });
  const { data: categoryData } = useGetMenuCategoriesQuery({ limit: 100 });

  const [createItem, { isLoading: creating }] = useCreateMenuItemMutation();
  const [updateItem, { isLoading: updating }] = useUpdateMenuItemMutation();
  const [deleteItem] = useDeleteMenuItemMutation();

  const categories = categoryData?.data ?? [];
  const categoryOptions = categories.map((row) => ({
    value: String(row.id),
    label: row.name,
  }));

  const columns = [
    { key: "name", label: "Item" },
    {
      key: "category",
      label: "Section",
      render: (category) => category?.name ?? "—",
    },
    { key: "price", label: "Price", render: (value) => formatMoney(value) },
    { key: "tax_rate", label: "GST", render: (value) => formatPercent(value, { decimals: 0 }) },
    {
      key: "is_veg",
      label: "Type",
      render: (value) => (value ? "Veg" : "Non-veg"),
    },
    {
      key: "is_available",
      label: "Today",
      render: (value) =>
        value ? (
          <span className="text-success">Available</span>
        ) : (
          <span className="text-muted-foreground">Sold out</span>
        ),
    },
  ];

  const filterConfig = [
    { name: "search", label: "Search", type: "text", placeholder: "Item or HSN code" },
    { name: "category_id", label: "Section", type: "select", options: categoryOptions },
    {
      name: "is_available",
      label: "Availability",
      type: "select",
      options: [
        { value: "true", label: "Available" },
        { value: "false", label: "Sold out" },
      ],
    },
  ];

  const formFields = [
    {
      name: "category_id",
      label: "Section",
      type: "select",
      options: categoryOptions,
      required: true,
    },
    { name: "name", label: "Item name", type: "text", required: true },
    { name: "description", label: "Description", type: "textarea", rows: 2 },
    {
      name: "price",
      label: "Price",
      type: "number",
      step: "0.01",
      min: "0.01",
      required: true,
      help: "What the customer is charged, before GST unless your prices are tax-inclusive.",
    },
    {
      name: "tax_rate",
      label: "GST slab",
      type: "select",
      options: GST_RATES,
      required: true,
      help: "Food served is 5%. A sealed bottle or a bag of beans is 18%.",
    },
    { name: "hsn_code", label: "HSN code", type: "text", help: "Required on a GST invoice above the turnover threshold." },
    {
      name: "is_veg",
      label: "Vegetarian",
      type: "select",
      options: [
        { value: "true", label: "Veg" },
        { value: "false", label: "Non-veg" },
      ],
    },
    {
      name: "is_available",
      label: "Available today",
      type: "select",
      options: [
        { value: "true", label: "Available" },
        { value: "false", label: "Sold out" },
      ],
    },
    { name: "prep_minutes", label: "Prep time (minutes)", type: "number", min: "0" },
  ];

  const toFormValues = (row) =>
    row
      ? {
          category_id: String(row.category_id ?? ""),
          name: row.name ?? "",
          description: row.description ?? "",
          price: row.price ?? "",
          tax_rate: String(Number(row.tax_rate ?? 5)),
          hsn_code: row.hsn_code ?? "",
          is_veg: String(Boolean(row.is_veg)),
          is_available: String(Boolean(row.is_available)),
          prep_minutes: row.prep_minutes ?? "",
        }
      : { tax_rate: "5", is_veg: "true", is_available: "true" };

  const toPayload = (values) => ({
    category_id: Number(values.category_id),
    name: values.name?.trim(),
    description: values.description || null,
    price: values.price,
    tax_rate: values.tax_rate,
    hsn_code: values.hsn_code || null,
    is_veg: values.is_veg === "true",
    is_available: values.is_available === "true",
    prep_minutes: values.prep_minutes === "" ? null : Number(values.prep_minutes),
  });

  const close = () => {
    setShowForm(false);
    setEditing(null);
  };

  const handleSubmit = async (values) => {
    try {
      const body = toPayload(values);
      if (editing) {
        await updateItem({ id: editing.id, ...body }).unwrap();
        toast.success(`${body.name} updated`);
      } else {
        await createItem(body).unwrap();
        toast.success(`${body.name} added to the menu`);
      }
      close();
    } catch (error) {
      toast.error(error?.data?.detail || "Could not save the item");
    }
  };

  const handleDelete = async (row) => {
    const ok = await confirm({
      title: `Take "${row.name}" off the menu?`,
      message:
        "It stops appearing on the order screen. Bills that already include it are unaffected — they keep the price they were sold at.",
      tone: "danger",
      confirmLabel: "Remove",
    });
    if (!ok) return;

    try {
      await deleteItem(row.id).unwrap();
      toast.success(`${row.name} removed`);
    } catch (error) {
      toast.error(error?.data?.detail || "Could not remove the item");
    }
  };

  const applyFilters = () => {
    setPage(1);
    setAppliedFilters(
      Object.fromEntries(Object.entries(filters).filter(([, value]) => value !== "")),
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-xl font-semibold text-foreground">Items</h2>
        {canCreate("menu") && (
          <Button label="Add item" onClick={() => setShowForm(true)} />
        )}
      </div>

      <FilterBar
        filters={filterConfig}
        values={filters}
        onChange={(key, value) => setFilters((prev) => ({ ...prev, [key]: value }))}
        onApply={applyFilters}
        onReset={() => {
          setFilters({});
          setAppliedFilters({});
          setPage(1);
        }}
      />

      <DataTable
        loading={isFetching}
        data={data?.data ?? []}
        columns={columns}
        caption="Menu items"
        emptyMessage="No items on the menu yet"
        emptyHint="Add your first item, or run `python manage.py seed-menu` for a starter menu you can edit."
        emptyAction={
          canCreate("menu") ? (
            <Button label="Add item" onClick={() => setShowForm(true)} />
          ) : null
        }
        onEdit={
          canUpdate("menu")
            ? (row) => {
                setEditing(row);
                setShowForm(true);
              }
            : undefined
        }
        onDelete={canDelete("menu") ? handleDelete : undefined}
        pagination={{
          currentPage: data?.currentPage ?? page,
          totalPages: data?.totalPages ?? 1,
          total: data?.total,
        }}
        onPageChange={setPage}
      />

      {showForm && (
        <Modal title={editing ? `Edit ${editing.name}` : "Add item"} onClose={close}>
          <DynamicForm
            fields={formFields}
            initialValues={toFormValues(editing)}
            onSubmit={handleSubmit}
            onCancel={close}
            submitting={creating || updating}
            submitLabel={editing ? "Save changes" : "Add to menu"}
          />
        </Modal>
      )}
    </div>
  );
};

export default MenuItems;
