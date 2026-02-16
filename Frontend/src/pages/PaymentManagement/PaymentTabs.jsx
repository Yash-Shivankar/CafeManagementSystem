import { useState } from "react";
import Payments from "./Payments";
import Earnings from "./Earnings";

const tabs = [
  { key: "payments", label: "Payments", component: Payments },
  { key: "earnings", label: "Earnings", component: Earnings },
];

const PaymentTabs = () => {
  const [activeTab, setActiveTab] = useState("payments");

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

export default PaymentTabs;
