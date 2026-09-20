import { useState } from "react";
import Tabs from "../../components/Tabs";
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

export default CustomerTabs;
