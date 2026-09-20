import { useState } from "react";
import { useConfirm } from "../../components/useConfirm";
import DataTable from "../../components/DataTable";
import FilterBar from "../../components/FilterBar";
import { toast } from "react-toastify";
import { usePermissions } from "../../services/usePermissions";

import {
  useGetSessionsQuery,
  useRevokeSessionMutation,
} from "../../app/allSlices";

const formatWhen = (value) => {
  if (!value) return "—";
  return new Date(value).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
};

const shortenAgent = (agent) => {
  if (!agent) return "Unknown device";

  const browser =
    /Edg\//.test(agent) ? "Edge"
    : /OPR\//.test(agent) ? "Opera"
    : /Chrome\//.test(agent) ? "Chrome"
    : /Safari\//.test(agent) ? "Safari"
    : /Firefox\//.test(agent) ? "Firefox"
    : "Browser";
  const platform =
    /Windows/.test(agent) ? "Windows"
    : /Android/.test(agent) ? "Android"
    : /iPhone|iPad/.test(agent) ? "iOS"
    : /Mac OS X/.test(agent) ? "macOS"
    : /Linux/.test(agent) ? "Linux"
    : "";
  return platform ? `${browser} on ${platform}` : browser;
};

const ActivityLogs = () => {
  const confirm = useConfirm();
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({});
  const [appliedFilters, setAppliedFilters] = useState({});

  const { canCreate } = usePermissions();
  const limit = 10;

  const { data, isLoading, refetch } = useGetSessionsQuery({
    page,
    limit,
    ...appliedFilters,
  });

  const [revokeSession] = useRevokeSessionMutation();

  const sessionFiltersConfig = [
    {
      name: "search",
      label: "Search",
      type: "text",
      placeholder: "Name, email or IP address",
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
    {
      key: "user",
      label: "User",
      render: (user) =>
        user
          ? `${user.first_name ?? ""} ${user.last_name ?? ""}`.trim() ||
            user.email ||
            `User ${user.id}`
          : "—",
    },
    {
      key: "user_agent",
      label: "Device",
      render: (value) => shortenAgent(value),
    },
    { key: "ip_address", label: "IP address" },
    {
      key: "created_at",
      label: "Signed in",
      render: (value) => formatWhen(value),
    },
    {
      key: "revoked_at",
      label: "Status",
      render: (value, row) => {
        if (value) return `Ended ${formatWhen(value)}`;
        if (new Date(row.expires_at) < new Date()) return "Expired";
        return "Active";
      },
    },
  ];

  const handleRevoke = async (row) => {
    if (row.revoked_at) {
      toast.info("That session has already ended");
      return;
    }
    if (!(await confirm({ message: "End this session? The user will have to sign in again." }))) {
      return;
    }try {
      await revokeSession(row.id).unwrap();
      toast.success("Session ended");
      refetch();
    } catch (e) {
      toast.error(e?.data?.detail || "Could not end that session");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Activity Log</h1>
          <p className="text-sm opacity-70">
            Sign-in history. Record-level changes are on the Change History
            tab.
          </p>
        </div>
      </div>

      <FilterBar
        filters={sessionFiltersConfig}
        values={filters}
        onChange={handleFilterChange}
        onApply={applyFilters}
        onReset={resetFilters}
      />

      <DataTable
        loading={isLoading}
        data={data?.data || []}
        columns={columns}

        onDelete={canCreate("activityLog") ? handleRevoke : undefined}
        pagination={{
          currentPage: data?.currentPage || page,
          totalPages: data?.totalPages || 1,
        }}
        onPageChange={setPage}
      />
    </div>
  );
};

export default ActivityLogs;
