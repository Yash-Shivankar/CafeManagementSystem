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
            <Route path="app-settings" element={<AppSettings />} />
          </Route>
        </Routes>
      </Router>
    </AppInitializer>
  );
}

export default App;
