import { lazy, Suspense } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { ToastContainer } from "react-toastify";

import MainLayout from "./components/MainLayout";
import ProtectedRoute from "./components/ProtectedRoute";
import AppInitializer from "./components/AppInitializer";
import ErrorBoundary from "./components/ErrorBoundary";
import ConfirmProvider from "./components/ConfirmProvider";
import "./index.css";

import Login from "./pages/Login";
import Register from "./pages/Register";

const Dashboard = lazy(() => import("./pages/Dashboard"));
const AppSettings = lazy(() => import("./pages/AppSettings"));
const Outlets = lazy(() => import("./pages/OutletManagement/Outlets"));
const UserTabs = lazy(() => import("./pages/UserManagement/UserTabs"));
const EmployeeTabs = lazy(() => import("./pages/EmployeeManagement/EmployeeTabs"));
const CustomerTabs = lazy(() => import("./pages/CustomerManagement/CustomerTabs"));
const EmployeePaymentTabs = lazy(
  () => import("./pages/EmployeePaymentManagement/EmployeePaymentTabs"),
);
const PaymentTabs = lazy(() => import("./pages/PaymentManagement/PaymentTabs"));
const InventoryTabs = lazy(() => import("./pages/InventoryManagement/InventoryTabs"));
const ActivityLogTabs = lazy(
  () => import("./pages/ActivityLogManagement/ActivityLogTabs"),
);
const Orders = lazy(() => import("./pages/OrderManagement/Orders"));
const KitchenDisplay = lazy(() => import("./pages/OrderManagement/KitchenDisplay"));
const MenuTabs = lazy(() => import("./pages/MenuManagement/MenuTabs"));
const NotFound = lazy(() => import("./pages/NotFound"));

const RouteFallback = () => (
  <div className="p-6 text-sm text-muted-foreground" role="status">
    Loading…
  </div>
);

const SCREENS = [
  { path: "dashboard", module: "dashboard", Screen: Dashboard },
  { path: "outlet-management", module: "outlets", Screen: Outlets },
  { path: "user-management", module: "users", Screen: UserTabs },
  { path: "employee-management", module: "employees", Screen: EmployeeTabs },
  { path: "orders", module: "orders", Screen: Orders },
  { path: "kitchen", module: "orders", Screen: KitchenDisplay },
  { path: "menu-management", module: "menu", Screen: MenuTabs },
  { path: "customer-management", module: "customers", Screen: CustomerTabs },
  { path: "inventory-management", module: "inventory", Screen: InventoryTabs },
  { path: "payment-management", module: "payments", Screen: PaymentTabs },
  {
    path: "employee-payment-management",
    module: "employeePayments",
    Screen: EmployeePaymentTabs,
  },
  { path: "app-settings", module: "settings", Screen: AppSettings },
  { path: "activity-log-management", module: "activityLog", Screen: ActivityLogTabs },
];

function App() {
  return (
    <ErrorBoundary>
      <AppInitializer>
        <ConfirmProvider>
          <ToastContainer position="top-right" newestOnTop />
          <Router basename={import.meta.env.BASE_URL}>
            <Suspense fallback={<RouteFallback />}>
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />

                <Route
                  path="/"
                  element={
                    <ProtectedRoute>
                      <MainLayout />
                    </ProtectedRoute>
                  }
                >
                  <Route index element={<Navigate to="/dashboard" replace />} />

                  {SCREENS.map(({ path, module, Screen }) => (
                    <Route
                      key={path}
                      path={path}
                      element={
                        <ProtectedRoute module={module}>
                          <Screen />
                        </ProtectedRoute>
                      }
                    />
                  ))}

                  <Route path="*" element={<NotFound />} />
                </Route>

                <Route path="*" element={<NotFound />} />
              </Routes>
            </Suspense>
          </Router>
        </ConfirmProvider>
      </AppInitializer>
    </ErrorBoundary>
  );
}

export default App;
