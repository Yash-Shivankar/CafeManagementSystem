import { useState } from "react";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import { toast } from "react-toastify";

import {
  useGetEmployeeAttendancesQuery,
  useCreateEmployeeAttendanceMutation,
  useUpdateEmployeeAttendanceMutation,
  useDeleteEmployeeAttendanceMutation,
  useGetEmployeeDetailsQuery,
} from "../../app/allSlices";

const EmployeeAttendances = () => {
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingAttendance, setEditingAttendance] = useState(null);

  const limit = 10;

  const { data, isLoading, refetch } = useGetEmployeeAttendancesQuery({
    page,
    limit,
  });
  const { data: detailsData } = useGetEmployeeDetailsQuery();

  const [createAttendance] = useCreateEmployeeAttendanceMutation();
  const [updateAttendance] = useUpdateEmployeeAttendanceMutation();
  const [deleteAttendance] = useDeleteEmployeeAttendanceMutation();

  const today = new Date().toISOString().split("T")[0];
  const attachTodayDate = (time) => {
    if (!time) return null;
    return `${today}T${time}`;
  };
  const extractTime = (datetime) => {
    if (!datetime) return "";
    return datetime.slice(11, 16);
  };

  const columns = [
    { key: "id", label: "Id" },
    {
      key: "employee",
      label: "Employee Name",
      render: (employee) =>
        `${employee?.user?.first_name ?? ""} ${employee?.user?.last_name ?? ""}`.trim(),
    },
    { key: "session", label: "Session" },
    {
      key: "check_in",
      label: "CheckIn",
      render: (value) =>
        value
          ? new Date(value).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })
          : "-",
    },
    {
      key: "check_out",
      label: "CheckOut",
      render: (value) =>
        value
          ? new Date(value).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })
          : "-",
    },
    { key: "status", label: "Status" },
  ];

  const attendancesFormFields = [
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
      name: "session",
      label: "Session",
      type: "select",
      options: [
        { label: "Session 1", value: "session_1" },
        { label: "Session 2", value: "session_2" },
      ],
    },
    {
      name: "check_in",
      label: "Check In",
      type: "time",
    },
    {
      name: "check_out",
      label: "Check Out",
      type: "time",
    },
    {
      name: "status",
      label: "Status",
      type: "select",
      options: [
        { label: "Present", value: "present" },
        { label: "Absent", value: "absent" },
        { label: "Leave", value: "leave" },
      ],
    },
  ];

  const handleSubmit = async (formData) => {
    try {
      if (editingAttendance) {
        await updateAttendance({
          id: editingAttendance.id,
          ...formData,
          date: editingAttendance.date || today,
          check_in: attachTodayDate(formData.check_in),
          check_out: attachTodayDate(formData.check_out),
        }).unwrap();
        toast.success("Employee Attendances updated successfully");
      } else {
        await createAttendance({
          ...formData,
          date: today,
          check_in: attachTodayDate(formData.check_in),
          check_out: attachTodayDate(formData.check_out),
        }).unwrap();
        toast.success("Employee Attendances created successfully");
      }
      refetch();
      setShowForm(false);
      setEditingAttendance(null);
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  const handleDelete = async (row) => {
    if (
      !window.confirm(
        "Are you sure you want to delete this employee attendances?",
      )
    )
      return;

    try {
      await deleteAttendance(row.id).unwrap();
      toast.success("Employee Attendances deleted successfully");
      refetch();
    } catch (e) {
      const errorMsg = e?.data?.detail || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  const buildInitialValues = (attendance) => {
    if (!attendance) return {};

    return {
      ...attendance,
      employee_id: attendance.employee?.id,
      check_in: extractTime(attendance.check_in),
      check_out: extractTime(attendance.check_out),
    };
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Employee Attendances</h1>
        <Button
          label="Add Employee Attendances"
          onClick={() => setShowForm(true)}
        />
      </div>

      <DataTable
        loading={isLoading}
        data={data?.data || []}
        columns={columns}
        onEdit={(row) => {
          setEditingAttendance(row);
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
            editingAttendance
              ? "Edit Employee Attendances"
              : "Create Employee Attendances"
          }
          onClose={() => {
            setShowForm(false);
            setEditingAttendance(null);
          }}
        >
          <DynamicForm
            fields={attendancesFormFields}
            initialValues={buildInitialValues(editingAttendance)}
            onSubmit={handleSubmit}
          />
        </Modal>
      )}
    </div>
  );
};

export default EmployeeAttendances;
