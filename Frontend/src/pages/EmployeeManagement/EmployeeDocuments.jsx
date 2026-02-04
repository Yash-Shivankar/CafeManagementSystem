import { useState } from "react";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import { toast } from "react-toastify";

import {
  useGetEmployeeDocumentsQuery,
  useCreateEmployeeDocumentMutation,
  useUpdateEmployeeDocumentMutation,
  useDeleteEmployeeDocumentMutation,
  useUploadFileMutation,
  useGetEmployeeDetailsQuery,
} from "../../app/allSlices";

const EmployeeDocuments = () => {
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingDocument, setEditingDocument] = useState(null);

  const limit = 10;

  const { data, isLoading, refetch } = useGetEmployeeDocumentsQuery({
    page,
    limit,
  });
  const { data: detailsData } = useGetEmployeeDetailsQuery();

  const [createDocument] = useCreateEmployeeDocumentMutation();
  const [updateDocument] = useUpdateEmployeeDocumentMutation();
  const [deleteDocument] = useDeleteEmployeeDocumentMutation();
  const [uploadDocument] = useUploadFileMutation();

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
    // { key: "doc_url", label: "Document Path" },
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

      // 1️⃣ Upload file
      if (formData.file instanceof File) {
        const filePayload = new FormData();
        filePayload.append("file", formData.file);

        uploadedFileData = await uploadDocument(filePayload).unwrap();
        console.log("Upload Response:", uploadedFileData);
      }

      // 2️⃣ Build payload using upload response
      const payload = {
        employee_id: formData.employee_id,
        filename: uploadedFileData?.filename,
        original_name: uploadedFileData?.original_name,
        size: String(uploadedFileData?.size),
        doc_type: formData.doc_type,
        doc_url: uploadedFileData?.doc_url,
      };

      // 3️⃣ Persist EmployeeDocument (NO FILE)
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
    if (
      !window.confirm(
        "Are you sure you want to delete this employee documents?",
      )
    )
      return;

    try {
      await deleteDocument(row.id).unwrap();
      toast.success("Employee Documents deleted successfully");
      refetch();
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Employee Documents</h1>
        <Button
          label="Add Employee Documents"
          onClick={() => setShowForm(true)}
        />
      </div>

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
            initialValues={editingDocument ? editingDocument : {}}
            onSubmit={handleSubmit}
          />
        </Modal>
      )}
    </div>
  );
};

export default EmployeeDocuments;
