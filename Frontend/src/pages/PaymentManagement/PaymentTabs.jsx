import { useState } from "react";
import Tabs from "../../components/Tabs";
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

export default PaymentTabs;
