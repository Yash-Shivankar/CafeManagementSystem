import { useState } from "react";
import Incentives from "./Incentives";
import Increments from "./Increments";
import SalaryPayments from "./SalaryPayments";
import SalaryStructures from "./SalaryStructures";

const tabs = [
  { key: "incentives", label: "Incentives", component: Incentives },
  {
    key: "salary_payments",
    label: "Salary Payments",
    component: SalaryPayments,
  },
  { key: "increments", label: "Increments", component: Increments },
  {
    key: "salary_structures",
    label: "Salary Structures",
    component: SalaryStructures,
  },
];

const EmployeePaymentTabs = () => {
  const [activeTab, setActiveTab] = useState("incentives");

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

export default EmployeePaymentTabs;
