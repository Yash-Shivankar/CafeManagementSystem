import { useState } from "react";
import Designations from "./Designations";
import Departments from "./Departments";
import EmployeeDetails from "./EmployeeDetails";
import EmployeeAttendances from "./EmployeeAttendances";
import EmployeeDocuments from "./EmployeeDocuments";
import EmployeePerformances from "./EmployeePerformances";

const tabs = [
  { key: "details", label: "Details", component: EmployeeDetails },
  { key: "attendance", label: "Attendance", component: EmployeeAttendances },
  { key: "documents", label: "Documents", component: EmployeeDocuments },
  { key: "performance", label: "Performance", component: EmployeePerformances },
  { key: "designations", label: "Designations", component: Designations },
  { key: "departments", label: "Departments", component: Departments },
];

const EmployeeTabs = () => {
  const [activeTab, setActiveTab] = useState("details");

  const ActiveComponent = tabs.find((tab) => tab.key === activeTab)?.component;

  return (
    <div className="p-4 space-y-6">
      {/* Tabs */}
      <div className="flex flex-wrap gap-6 border-b">
        {tabs.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            className={`pb-2 transition-all ${
              activeTab === key ? "border-b-2 border-blue-500 font-bold" : ""
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="pt-2">{ActiveComponent && <ActiveComponent />}</div>
    </div>
  );
};

export default EmployeeTabs;
