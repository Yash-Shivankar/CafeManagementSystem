import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { ToastContainer } from "react-toastify";
import Login from "./pages/Login";
import Register from "./pages/Register";
import MainLayout from "./components/MainLayout";
import ProtectedRoute from "./components/ProtectedRoute";
import AppInitializer from "./components/AppInitializer";
import Dashboard from "./pages/Dashboard";
import AppSettings from "./pages/AppSettings";
import UserTabs from "./pages/UserManagement/UserTabs";
import EmployeeTabs from "./pages/EmployeeManagement/EmployeeTabs";
import CustomerTabs from "./pages/CustomerManagement/CustomerTabs";
import EmployeePaymentTabs from "./pages/EmployeePaymentManagement/EmployeePaymentTabs";
import PaymentTabs from "./pages/PaymentManagement/PaymentTabs";
import InventoryTabs from "./pages/InventoryManagement/InventoryTabs";
import ActivityLogs from "./pages/ActivityLogManagement/ActivityLogs";
import "./index.css";

function App() {
  return (
    <AppInitializer>
      <ToastContainer />
      <Router>
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
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="user-management" element={<UserTabs />} />
            <Route path="employee-management" element={<EmployeeTabs />} />
            <Route path="customer-management" element={<CustomerTabs />} />
            <Route path="inventory-management" element={<InventoryTabs />} />
            <Route path="payment-management" element={<PaymentTabs />} />
            <Route
              path="employee-payment-management"
              element={<EmployeePaymentTabs />}
            />
            <Route path="app-settings" element={<AppSettings />} />
            <Route path="activity-log-management" element={<ActivityLogs />} />
          </Route>
        </Routes>
      </Router>
    </AppInitializer>
  );
}

export default App;
