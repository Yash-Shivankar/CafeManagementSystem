import { useState } from "react";
import { toast } from "react-toastify";

import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import { useConfirm } from "../../components/useConfirm";
import { usePermissions } from "../../services/usePermissions";
import {
  useCreateMenuCategoryMutation,
  useDeleteMenuCategoryMutation,
  useGetMenuCategoriesQuery,
  useUpdateMenuCategoryMutation,
} from "../../app/allSlices";

const MenuCategories = () => {
  const confirm = useConfirm();
  const { canCreate, canUpdate, canDelete } = usePermissions();

  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);

  const limit = 10;
  const { data, isFetching } = useGetMenuCategoriesQuery({ page, limit });

  const [createCategory, { isLoading: creating }] = useCreateMenuCategoryMutation();
  const [updateCategory, { isLoading: updating }] = useUpdateMenuCategoryMutation();
  const [deleteCategory] = useDeleteMenuCategoryMutation();

  const columns = [
    { key: "sort_order", label: "Order" },
    { key: "name", label: "Section" },
    { key: "description", label: "Description", render: (value) => value || "—" },
    {
      key: "outlet_id",
      label: "Scope",
      render: (value) => (value ? "This outlet" : "All outlets"),
    },
    {
      key: "is_active",
      label: "Status",
      render: (value) =>
        value ? (
          <span className="text-success">On the menu</span>
        ) : (
          <span className="text-muted-foreground">Hidden</span>
        ),
    },
  ];

  const formFields = [
    { name: "name", label: "Section name", type: "text", required: true },
    { name: "description", label: "Description", type: "textarea", rows: 2 },
    {
      name: "sort_order",
      label: "Position",
      type: "number",
      min: "0",
      help: "Lower numbers appear first. Menus are read in a deliberate order.",
    },
    {
      name: "is_active",
      label: "On the menu",
      type: "select",
      options: [
        { value: "true", label: "Yes" },
        { value: "false", label: "Hidden for now" },
      ],
    },
  ];

  const close = () => {
    setShowForm(false);
    setEditing(null);
  };

  const handleSubmit = async (values) => {
    const body = {
      name: values.name?.trim(),
      description: values.description || null,
      sort_order: Number(values.sort_order || 0),
      is_active: values.is_active !== "false",
    };

    try {
      if (editing) {
        await updateCategory({ id: editing.id, ...body }).unwrap();
        toast.success(`${body.name} updated`);
      } else {
        await createCategory(body).unwrap();
        toast.success(`${body.name} added`);
      }
      close();
    } catch (error) {
      toast.error(error?.data?.detail || "Could not save the section");
    }
  };

  const handleDelete = async (row) => {
    const ok = await confirm({
      title: `Delete the "${row.name}" section?`,
      message:
        "Only an empty section can be deleted. If it still has items, hide it instead — a seasonal section comes back, and its sales history has to survive the winter.",
      tone: "danger",
      confirmLabel: "Delete",
    });
    if (!ok) return;

    try {
      await deleteCategory(row.id).unwrap();
      toast.success(`${row.name} deleted`);
    } catch (error) {
      toast.error(error?.data?.detail || "Could not delete the section");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-xl font-semibold text-foreground">Sections</h2>
        {canCreate("menu") && (
          <Button label="Add section" onClick={() => setShowForm(true)} />
        )}
      </div>

      <DataTable
        loading={isFetching}
        data={data?.data ?? []}
        columns={columns}
        caption="Menu sections"
        emptyMessage="No sections yet"
        emptyHint="A section groups items on the order screen — Hot Coffee, Bakery, Retail."
        emptyAction={
          canCreate("menu") ? (
            <Button label="Add section" onClick={() => setShowForm(true)} />
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
        <Modal title={editing ? `Edit ${editing.name}` : "Add section"} onClose={close}>
          <DynamicForm
            fields={formFields}
            initialValues={
              editing
                ? {
                    name: editing.name ?? "",
                    description: editing.description ?? "",
                    sort_order: editing.sort_order ?? 0,
                    is_active: String(Boolean(editing.is_active)),
                  }
                : { sort_order: 0, is_active: "true" }
            }
            onSubmit={handleSubmit}
            onCancel={close}
            submitting={creating || updating}
            submitLabel={editing ? "Save changes" : "Add section"}
          />
        </Modal>
      )}
    </div>
  );
};

export default MenuCategories;
