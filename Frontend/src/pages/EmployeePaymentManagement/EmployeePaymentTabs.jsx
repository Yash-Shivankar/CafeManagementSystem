import { useState } from "react";
import Tabs from "../../components/Tabs";
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
      <Tabs tabs={tabs} activeKey={activeTab} onChange={setActiveTab} />

      <div
        role="tabpanel"
        id={`tabpanel-${activeTab}`}
        aria-labelledby={`tab-${activeTab}`}
        className="pt-2"
      >
        {ActiveComponent && <ActiveComponent />}
      </div>
    </div>
  );
};

export default EmployeePaymentTabs;
