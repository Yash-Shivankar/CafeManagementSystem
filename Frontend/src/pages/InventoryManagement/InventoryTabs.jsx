import { useState } from "react";
import Tabs from "../../components/Tabs";
import InventoryCategories from "./InventoryCategories";
import InventoryLogs from "./InventoryLogs";
import InventoryItems from "./InventoryItems";

const tabs = [
  {
    key: "inventory_items",
    label: "Items",
    component: InventoryItems,
  },
  {
    key: "inventory_categories",
    label: "Categories",
    component: InventoryCategories,
  },
  { key: "inventory_logs", label: "Logs", component: InventoryLogs },
];

const InventoryTabs = () => {
  const [activeTab, setActiveTab] = useState("inventory_items");

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

export default InventoryTabs;
