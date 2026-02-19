import { Users, UserCheck, User, Package } from "lucide-react";

import { useGetDashboardStatsQuery } from "../app/allSlices";
import StatsCard from "../components/StatsCard";

const Dashboard = () => {
  const { data, isLoading } = useGetDashboardStatsQuery();

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          label="Active Users"
          value={data?.users_count}
          loading={isLoading}
          icon={Users}
          iconSize="xxl"
          className="h-32"
        />

        <StatsCard
          label="Employees"
          value={data?.employees_count}
          loading={isLoading}
          icon={UserCheck}
          iconSize="xxl"
          className="h-32"
        />

        <StatsCard
          label="Customers"
          value={data?.customers_count}
          loading={isLoading}
          icon={User}
          iconSize="xxl"
          className="h-32"
        />

        <StatsCard
          label="Inventory Items"
          value={data?.items_count}
          loading={isLoading}
          icon={Package}
          iconSize="xxl"
          className="h-32"
        />
      </div>
    </div>
  );
};

export default Dashboard;
