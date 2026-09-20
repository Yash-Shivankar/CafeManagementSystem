import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQueryWithReauth } from "./baseQuery";

export const TAG_TYPES = [
  "Bookings",
  "Outlets",
  "Sessions",
  "AuditLogs",
  "CustomerFeedbacks",
  "CustomerInvoices",
  "Dashboard",
  "Departments",
  "Designations",
  "Earning",
  "EmployeeAttendances",
  "EmployeeDetails",
  "EmployeeDocuments",
  "EmployeePerformances",
  "Files",
  "Incentives",
  "IncrementHistories",
  "InventoryCategories",
  "InventoryItems",
  "InventoryLogs",
  "Kitchen",
  "MenuCategories",
  "MenuItems",
  "Orders",
  "Payments",
  "Roles",
  "SalaryPayments",
  "SalaryStructures",
  "Services",
  "Settings",
  "Tables",
  "Users",
];

export const baseApi = createApi({
  reducerPath: "allSlices",
  baseQuery: baseQueryWithReauth,
  tagTypes: TAG_TYPES,
  endpoints: () => ({}),
});

export default baseApi;
