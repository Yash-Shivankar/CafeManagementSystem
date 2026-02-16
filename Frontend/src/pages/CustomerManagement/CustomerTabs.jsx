import { useState } from "react";
import CustomerFeedbacks from "./CustomerFeedbacks";
import CustomerInvoices from "./CustomerInvoices";
import Services from "./Services";
import Tables from "./Tables";

const tabs = [
  { key: "invoices", label: "Invoices", component: CustomerInvoices },
  { key: "feedbacks", label: "Feedback", component: CustomerFeedbacks },
  { key: "services", label: "Services", component: Services },
  { key: "tables", label: "Tables", component: Tables },
];

const CustomerTabs = () => {
  const [activeTab, setActiveTab] = useState("invoices");

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

export default CustomerTabs;
