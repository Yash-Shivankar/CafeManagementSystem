// config/sidebarMenu.js
import { Home, Users, Settings } from "lucide-react";

export const sidebarMenu = [
  {
    label: "Dashboard",
    path: "/dashboard",
    icon: Home,
    module: "dashboard",
  },
  {
    label: "Users",
    path: "/users",
    icon: Users,
    module: "users",
  },
  {
    label: "Application Settings",
    path: "/settings",
    icon: Settings,
    module: "settings",
  },
];
