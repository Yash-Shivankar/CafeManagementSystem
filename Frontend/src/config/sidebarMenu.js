// config/sidebarMenu.js
import {
  Home,
  Users,
  Settings,
  LayoutDashboard,
  Activity,
  UserCog,
  UserCheck,
  Package,
  CreditCard,
} from "lucide-react";

export const sidebarMenu = [
  {
    label: "Dashboard",
    path: "/dashboard",
    icon: Home,
    module: "dashboard",
  },
  {
    label: "Users",
    path: "/user-management",
    icon: Users,
    module: "users",
  },
  {
    label: "Employees",
    path: "/employee-management",
    icon: UserCheck,
    module: "employees",
  },
  {
    label: "Customers",
    path: "/customer-management",
    icon: Users,
    module: "customers",
  },
  {
    label: "Inventory",
    path: "/inventory-management",
    icon: Package,
    module: "inventory",
  },
  {
    label: "Payments",
    path: "/payment-management",
    icon: CreditCard,
    module: "payments",
  },
  {
    label: "Employee Payments",
    path: "/employee-payment-management",
    icon: CreditCard,
    module: "employeePayments",
  },
  {
    label: "Application Settings",
    path: "/app-settings",
    icon: Settings,
    module: "settings",
  },
  {
    label: "Activity Logs",
    path: "/activity-log-management",
    icon: Activity,
    module: "activityLog",
  },
];
