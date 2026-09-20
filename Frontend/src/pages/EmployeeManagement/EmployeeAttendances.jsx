import { useState } from "react";
import { formatDate, formatTime } from "../../utils/format";
import { useConfirm } from "../../components/useConfirm";
import DataTable from "../../components/DataTable";
import DynamicForm from "../../components/DynamicForm";
import Modal from "../../components/Modal";
import Button from "../../components/Button";
import FilterBar from "../../components/FilterBar";
import { toast } from "react-toastify";

import {
  useGetEmployeeAttendancesQuery,
  useCreateEmployeeAttendanceMutation,
  useUpdateEmployeeAttendanceMutation,
  useDeleteEmployeeAttendanceMutation,
  useGetEmployeeDetailsQuery,
} from "../../app/allSlices";

const EmployeeAttendances = () => {
  const confirm = useConfirm();
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingAttendance, setEditingAttendance] = useState(null);
  const [filters, setFilters] = useState({});
  const [appliedFilters, setAppliedFilters] = useState({});

  const limit = 10;

  const { data, isLoading, refetch } = useGetEmployeeAttendancesQuery({
    page,
    limit,
    ...appliedFilters,
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

  const attendanceFiltersConfig = [
    {
      name: "search",
      label: "Search",
      type: "text",
      placeholder: "Employee Name",
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
      name: "status",
      label: "Status",
      type: "select",
      options: [
        { label: "Present", value: "present" },
        { label: "Absent", value: "absent" },
        { label: "Leave", value: "leave" },
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
      key: "employee",
      label: "Employee Name",
      render: (employee) =>
        `${employee?.user?.first_name ?? ""} ${employee?.user?.last_name ?? ""}`.trim(),
    },
    {
      key: "date",
      label: "Date",
      render: (value) => formatDate(value),
    },
    { key: "session", label: "Session" },
    {
      key: "check_in",
      label: "CheckIn",
      render: (value) => formatTime(value),
    },
    {
      key: "check_out",
      label: "CheckOut",
      render: (value) => formatTime(value),
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
    if (!(await confirm({
        title: "Delete this attendance record?",
        message:
          "It will stop appearing in lists and reports. This cannot be undone from the app.",
        tone: "danger",
        confirmLabel: "Delete",
        }))) {
      return;
    }try {
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
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Employee Attendances</h1>
        <Button
          label="Add Employee Attendances"
          onClick={() => setShowForm(true)}
        />
      </div>

      <FilterBar
        filters={attendanceFiltersConfig}
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
