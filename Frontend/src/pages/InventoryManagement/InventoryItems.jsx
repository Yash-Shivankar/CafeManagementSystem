import { useState } from "react";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import { toast } from "react-toastify";

import {
  useGetInventoryItemsQuery,
  useCreateInventoryItemMutation,
  useUpdateInventoryItemMutation,
  useDeleteInventoryItemMutation,
  useGetInventoryCategoriesQuery,
} from "../../app/allSlices";

const InventoryItems = () => {
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  const limit = 10;

  const { data, isLoading, refetch } = useGetInventoryItemsQuery({
    page,
    limit,
  });

  const { data: categoriesData } = useGetInventoryCategoriesQuery();

  const [createItem] = useCreateInventoryItemMutation();
  const [updateItem] = useUpdateInventoryItemMutation();
  const [deleteItem] = useDeleteInventoryItemMutation();

  const columns = [
    { key: "id", label: "Id" },
    { key: "name", label: "Name" },
    {
      key: "category",
      label: "Category",
      render: (category) => category?.category_name || "-",
    },
    { key: "quantity", label: "Quantity" },
    { key: "min_quantity", label: "Minimum Quantity" },
    {
      key: "cost_price",
      label: "Cost Price",
      render: (value) => `₹ ${Number(value).toFixed(2)}`,
    },
    {
      key: "selling_price",
      label: "Selling Price",
      render: (value) => `₹ ${Number(value).toFixed(2)}`,
    },
  ];

  const itemFormFields = [
    {
      name: "name",
      label: "Item Name",
      type: "text",
      required: true,
    },

    {
      name: "category_id",
      label: "Category",
      type: "select",
      options:
        categoriesData?.data?.map((c) => ({
          label: c.category_name,
          value: c.id,
        })) || [],
      required: true,
    },

    {
      name: "quantity",
      label: "Quantity",
      type: "number",
      min: 0,
      step: 1,
    },

    {
      name: "min_quantity",
      label: "Minimum Quantity",
      type: "number",
      min: 0,
      step: 1,
    },

    {
      name: "cost_price",
      label: "Cost Price",
      type: "number",
      min: 0.01,
      step: "0.01",
      required: true,
    },

    {
      name: "selling_price",
      label: "Selling Price",
      type: "number",
      min: 0.01,
      step: "0.01",
      required: true,
    },
  ];

  const handleSubmit = async (formData) => {
    try {
      if (editingItem) {
        await updateItem({
          id: editingItem.id,
          ...formData,
        }).unwrap();
        toast.success("Item updated successfully");
      } else {
        await createItem(formData).unwrap();
        toast.success("Item created successfully");
      }
      refetch();
      setShowForm(false);
      setEditingItem(null);
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  const handleDelete = async (row) => {
    if (!window.confirm("Are you sure you want to delete this item?")) return;

    try {
      await deleteItem(row.id).unwrap();
      toast.success("Item deleted successfully");
      refetch();
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Items</h1>
        <Button label="Add Item" onClick={() => setShowForm(true)} />
      </div>

      <DataTable
        loading={isLoading}
        data={data?.data || []}
        columns={columns}
        onEdit={(row) => {
          setEditingItem(row);
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
          title={editingItem ? "Edit Item" : "Create Item"}
          onClose={() => {
            setShowForm(false);
            setEditingItem(null);
          }}
        >
          <DynamicForm
            fields={itemFormFields}
            initialValues={
              editingItem
                ? {
                    ...editingItem,
                    category_id: editingItem.category?.id,
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

export default InventoryItems;
