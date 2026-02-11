import { useState } from "react";
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
    <div className="p-6 space-y-6">
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

export default InventoryTabs;
