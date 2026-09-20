export const VIEW = "view";
export const CREATE = "create";
export const UPDATE = "update";
export const DELETE = "delete";

export const CRUD = [VIEW, CREATE, UPDATE, DELETE];

export const MODULES = [
  "dashboard",
  "users",
  "employees",
  "employeePayments",
  "customers",
  "inventory",
  "menu",
  "orders",
  "payments",
  "settings",
  "activityLog",
  "common",
  "media",
];

export const can = (user, module, action) =>
  Array.isArray(user?.permissions?.[module]) &&
  user.permissions[module].includes(action);

export const canView = (user, module) => can(user, module, VIEW);
export const canCreate = (user, module) => can(user, module, CREATE);
export const canUpdate = (user, module) => can(user, module, UPDATE);
export const canDelete = (user, module) => can(user, module, DELETE);
