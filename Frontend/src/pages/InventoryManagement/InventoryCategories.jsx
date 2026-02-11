import { useState } from "react";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import { toast } from "react-toastify";

import {
  useGetInventoryCategoriesQuery,
  useCreateInventoryCategoryMutation,
  useUpdateInventoryCategoryMutation,
  useDeleteInventoryCategoryMutation,
} from "../../app/allSlices";

const InventoryCategories = () => {
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);

  const limit = 10;

  const { data, isLoading, refetch } = useGetInventoryCategoriesQuery({
    page,
    limit,
  });

  const [createCategory] = useCreateInventoryCategoryMutation();
  const [updateCategory] = useUpdateInventoryCategoryMutation();
  const [deleteCategory] = useDeleteInventoryCategoryMutation();

  const columns = [
    { key: "id", label: "Id" },
    { key: "category_name", label: "Category Name" },
  ];

  const categoryFormFields = [
    { name: "category_name", label: "Category Name", type: "text" },
  ];

  const handleSubmit = async (formData) => {
    try {
      if (editingCategory) {
        await updateCategory({
          id: editingCategory.id,
          ...formData,
        }).unwrap();
        toast.success("Category updated successfully");
      } else {
        await createCategory(formData).unwrap();
        toast.success("Category created successfully");
      }
      refetch();
      setShowForm(false);
      setEditingCategory(null);
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  const handleDelete = async (row) => {
    if (!window.confirm("Are you sure you want to delete this category?"))
      return;

    try {
      await deleteCategory(row.id).unwrap();
      toast.success("Category deleted successfully");
      refetch();
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Categories</h1>
        <Button label="Add Category" onClick={() => setShowForm(true)} />
      </div>

      <DataTable
        loading={isLoading}
        data={data?.data || []}
        columns={columns}
        onEdit={(row) => {
          setEditingCategory(row);
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
          title={editingCategory ? "Edit Category" : "Create Category"}
          onClose={() => {
            setShowForm(false);
            setEditingCategory(null);
          }}
        >
          <DynamicForm
            fields={categoryFormFields}
            initialValues={editingCategory ? editingCategory : {}}
            onSubmit={handleSubmit}
          />
        </Modal>
      )}
    </div>
  );
};

export default InventoryCategories;
