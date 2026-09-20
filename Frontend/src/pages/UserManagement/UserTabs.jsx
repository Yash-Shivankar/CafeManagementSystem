import { useState } from "react";
import Tabs from "../../components/Tabs";
import Users from "./Users";
import Roles from "./Roles";

const tabs = [
  { key: "users", label: "Users", component: Users },
  { key: "roles", label: "Roles", component: Roles },
];

const UsersTabs = () => {
  const [activeTab, setActiveTab] = useState("users");
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

export default UsersTabs;
