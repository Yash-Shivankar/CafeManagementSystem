import { useState } from "react";
import { NavLink } from "react-router-dom";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { sidebarMenu } from "../config/sidebarMenu";
import { usePermissions } from "../services/usePermissions";

const Sidebar = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { canView } = usePermissions();

  const visibleMenu = sidebarMenu.filter((item) => canView(item.module));

  return (
    <aside
      className={`
        h-screen border-r transition-all duration-300
        ${collapsed ? "w-16" : "w-56"}
      `}
      style={{
        backgroundColor: "rgb(var(--color-surface))",
        borderColor: "rgb(var(--color-border))",
        color: "rgb(var(--color-text-primary))",
      }}
    >

      <div
        className="flex items-center justify-between px-3 py-2 border-b"
        style={{ borderColor: "rgb(var(--color-border))" }}
      >
        {!collapsed && (
          <span className="text-sm font-semibold tracking-wide">Menu</span>
        )}

        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1 rounded-md transition hover:opacity-80"
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      <nav className="py-2">
        <ul className="space-y-1 px-2">
          {visibleMenu.map((item) => {
            const Icon = item.icon;

            return (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  title={collapsed ? item.label : ""}
                  className={({ isActive }) =>
                    `
                      flex items-center gap-3 px-3 py-2 rounded-lg text-sm
                      transition-all duration-200
                      ${collapsed ? "justify-center" : ""}
                      ${
                        isActive
                          ? "font-medium shadow"
                          : "opacity-80 hover:opacity-100"
                      }
                    `
                  }
                  style={({ isActive }) => ({
                    backgroundColor: isActive
                      ? "rgb(var(--color-primary))"
                      : "transparent",
                    color: isActive
                      ? "rgb(var(--color-text-primary))"
                      : "rgb(var(--color-text-secondary))",
                  })}
                >
                  <Icon size={16} className="shrink-0" />
                  {!collapsed && <span>{item.label}</span>}
                </NavLink>
              </li>
            );
          })}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;
