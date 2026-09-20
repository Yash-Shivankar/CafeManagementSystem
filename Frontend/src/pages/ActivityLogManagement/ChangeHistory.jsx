import { useState } from "react";
import DataTable from "../../components/DataTable";
import FilterBar from "../../components/FilterBar";

import { useGetAuditLogsQuery } from "../../app/allSlices";

const TABLE_LABELS = {
  customer_invoices: "Invoices",
  payments: "Payments",
  inventory_items: "Inventory items",
  inventory_logs: "Stock movements",
  employee_details: "Employees",
  salary_payments: "Salary payments",
  profit_loss: "Profit & loss",
  users: "Users",
  departments: "Departments",
  designations: "Designations",
  bookings: "Bookings",
  tables: "Tables",
  services: "Services",
  outlets: "Outlets",
  roles: "Roles",
};

const ACTION_LABELS = {
  create: "Created",
  update: "Changed",
  delete: "Deleted",
};

const formatWhen = (value) =>
  value
    ? new Date(value).toLocaleString(undefined, {
        dateStyle: "medium",
        timeStyle: "short",
      })
    : "—";

const humanField = (field) =>
  field.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

const describeChanges = (changes) => {
  if (!changes || Object.keys(changes).length === 0) return "—";
  return Object.entries(changes)
    .map(
      ([field, move]) =>
        `${humanField(field)}: ${move?.from ?? "—"} → ${move?.to ?? "—"}`,
    )
    .join("; ");
};

const ChangeHistory = () => {
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({});
  const [appliedFilters, setAppliedFilters] = useState({});

  const limit = 10;

  const { data, isLoading } = useGetAuditLogsQuery({
    page,
    limit,
    ...appliedFilters,
  });

  const filtersConfig = [
    {
      name: "search",
      label: "Search",
      type: "text",
      placeholder: "Who, or which table",
    },
    {
      name: "table_name",
      label: "Record type",
      type: "select",
      options: Object.entries(TABLE_LABELS).map(([value, label]) => ({
        value,
        label,
      })),
    },
    {
      name: "action",
      label: "Action",
      type: "select",
      options: [
        { value: "create", label: "Created" },
        { value: "update", label: "Changed" },
        { value: "delete", label: "Deleted" },
      ],
    },
    { name: "start_date", label: "From", type: "date" },
    { name: "end_date", label: "To", type: "date" },
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
    {
      key: "created_at",
      label: "When",
      render: (value) => formatWhen(value),
    },
    {
      key: "actor",
      label: "Who",
      render: (actor, row) =>
        actor
          ? `${actor.first_name ?? ""} ${actor.last_name ?? ""}`.trim() ||
            actor.email ||
            `User ${actor.id}`
          : row.actor_role || "System",
    },
    {
      key: "action",
      label: "Action",
      render: (value) => ACTION_LABELS[value] || value,
    },
    {
      key: "table_name",
      label: "Record",
      render: (value, row) =>
        `${TABLE_LABELS[value] || value}${row.record_id ? ` #${row.record_id}` : ""}`,
    },
    {
      key: "changes",
      label: "What changed",
      render: (value) => describeChanges(value),
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold">Change history</h2>
        <p className="text-sm opacity-70">
          Every create, change and delete, with the previous value. Append-only —
          entries cannot be edited or removed.
        </p>
      </div>

      <FilterBar
        filters={filtersConfig}
        values={filters}
        onChange={handleFilterChange}
        onApply={applyFilters}
        onReset={resetFilters}
      />

      <DataTable
        loading={isLoading}
        data={data?.data || []}
        columns={columns}
        pagination={{
          currentPage: data?.currentPage || page,
          totalPages: data?.totalPages || 1,
        }}
        onPageChange={setPage}
      />
    </div>
  );
};

export default ChangeHistory;
