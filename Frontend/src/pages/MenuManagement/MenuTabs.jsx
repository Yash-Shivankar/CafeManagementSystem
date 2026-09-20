import { useState } from "react";
import Tabs from "../../components/Tabs";
import MenuItems from "./MenuItems";
import MenuCategories from "./MenuCategories";

const tabs = [
  { key: "items", label: "Items", component: MenuItems },
  { key: "sections", label: "Sections", component: MenuCategories },
];

const MenuTabs = () => {
  const [activeTab, setActiveTab] = useState("items");
  const ActiveComponent = tabs.find((tab) => tab.key === activeTab)?.component;

  return (
    <div className="p-4 space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold text-foreground">Menu</h1>
        <p className="text-sm text-muted-foreground">
          What you sell, what it costs, and which GST slab it is on.
        </p>
      </div>

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

export default MenuTabs;
