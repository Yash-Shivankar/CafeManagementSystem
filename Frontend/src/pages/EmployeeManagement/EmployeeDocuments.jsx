import { useState } from "react";
import { useConfirm } from "../../components/useConfirm";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import FilterBar from "../../components/FilterBar";
import { toast } from "react-toastify";
import { BaseUrl } from "../../config/config";

import {
  useGetEmployeeDocumentsQuery,
  useCreateEmployeeDocumentMutation,
  useUpdateEmployeeDocumentMutation,
  useDeleteEmployeeDocumentMutation,
  useUploadFileMutation,
  useGetEmployeeDetailsQuery,
} from "../../app/allSlices";

const EmployeeDocuments = () => {
  const confirm = useConfirm();
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingDocument, setEditingDocument] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [previewType, setPreviewType] = useState(null);
  const [filters, setFilters] = useState({});
  const [appliedFilters, setAppliedFilters] = useState({});

  const limit = 10;

  const { data, isLoading, refetch } = useGetEmployeeDocumentsQuery({
    page,
    limit,
    ...appliedFilters,
  });
  const { data: detailsData } = useGetEmployeeDetailsQuery();

  const [createDocument] = useCreateEmployeeDocumentMutation();
  const [updateDocument] = useUpdateEmployeeDocumentMutation();
  const [deleteDocument] = useDeleteEmployeeDocumentMutation();
  const [uploadDocument] = useUploadFileMutation();

  const documentsFiltersConfig = [
    {
      name: "search",
      label: "Search",
      type: "text",
      placeholder: "Employee Name / Filename / Orginal Name / Document Type",
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
      key: "employee",
      label: "Employee Name",
      render: (employee) =>
        `${employee?.user?.first_name ?? ""} ${employee?.user?.last_name ?? ""}`.trim(),
    },
    {
      key: "filename",
      label: "Filename",
    },
    { key: "original_name", label: "Orginal Name" },
    { key: "doc_type", label: "Document Type" },
    {
      key: "size",
      label: "Size",
    },
    {
      key: "doc_url",
      label: "Document",
      render: (url, row) => {
        if (!url) return "-";

        const fullUrl = `${BaseUrl}${url}`;
        const ext = row.original_name?.split(".").pop()?.toLowerCase();

        return (
          <Button
            size="sm"
            label="Preview"
            onClick={() => {
              setPreviewUrl(fullUrl);
              setPreviewType(ext);
            }}
          />
        );
      },
    },
  ];

  const documentsFormFields = [
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
    },
    {
      name: "doc_type",
      label: "Document Type",
      type: "text",
    },
    {
      name: "file",
      label: "Upload Document",
      type: "file",
    },
  ];

  const handleSubmit = async (formData) => {
    try {
      let uploadedFileData = null;

      if (formData.file instanceof File) {
        const filePayload = new FormData();
        filePayload.append("file", formData.file);

        uploadedFileData = await uploadDocument(filePayload).unwrap();
        console.log("Upload Response:", uploadedFileData);
      }

      const payload = {
        employee_id: formData.employee_id,
        filename: uploadedFileData?.filename,
        original_name: uploadedFileData?.original_name,
        size: String(uploadedFileData?.size),
        doc_type: formData.doc_type,
        doc_url: uploadedFileData?.doc_url,
      };

      if (editingDocument) {
        await updateDocument({
          id: editingDocument.id,
          ...payload,
        }).unwrap();
        toast.success("Employee Documents updated successfully");
      } else {
        await createDocument(payload).unwrap();
        toast.success("Employee Documents created successfully");
      }

      refetch();
      setShowForm(false);
      setEditingDocument(null);
    } catch (e) {
      console.error(e);
      toast.error(e?.data?.detail || "Something went wrong");
    }
  };

  const handleDelete = async (row) => {
    if (!(await confirm({
        title: "Delete this document?",
        message:
          "It will stop appearing in lists and reports. This cannot be undone from the app.",
        tone: "danger",
        confirmLabel: "Delete",
        }))) {
      return;
    }try {
      await deleteDocument(row.id).unwrap();
      toast.success("Employee Documents deleted successfully");
      refetch();
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Employee Documents</h1>
        <Button
          label="Add Employee Documents"
          onClick={() => setShowForm(true)}
        />
      </div>

      <FilterBar
        filters={documentsFiltersConfig}
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
          setEditingDocument(row);
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
          title={
            editingDocument
              ? "Edit Employee Documents"
              : "Create Employee Documents"
          }
          onClose={() => {
            setShowForm(false);
            setEditingDocument(null);
          }}
        >
          <DynamicForm
            fields={documentsFormFields}
            initialValues={
              editingDocument
                ? {
                    ...editingDocument,
                    employee_id: editingDocument.employee?.id,
                  }
                : {}
            }
            onSubmit={handleSubmit}
          />
        </Modal>
      )}

      {previewUrl && (
        <Modal
          title="Document Preview"
          onClose={() => {
            setPreviewUrl(null);
            setPreviewType(null);
          }}
        >

          {previewType === "pdf" && (
            <iframe src={previewUrl} className="w-full h-[80vh] border" />
          )}

          {["jpg", "jpeg", "png", "webp"].includes(previewType) && (
            <img
              src={previewUrl}
              alt="Preview"
              className="max-h-[80vh] mx-auto"
            />
          )}

          {!["pdf", "jpg", "jpeg", "png", "webp"].includes(previewType) && (
            <div className="text-center text-muted-foreground">
              Preview not supported for this file type
              <div className="mt-2">
                <a
                  href={previewUrl}
                  className="underline text-blue-600"
                  download
                >
                  Download instead
                </a>
              </div>
            </div>
          )}
        </Modal>
      )}
    </div>
  );
};

export default EmployeeDocuments;
