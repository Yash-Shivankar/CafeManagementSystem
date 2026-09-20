import { useState } from "react";
import Tabs from "../../components/Tabs";
import ActivityLogs from "./ActivityLogs";
import ChangeHistory from "./ChangeHistory";

const tabs = [
  { key: "sessions", label: "Sign-ins", component: ActivityLogs },
  { key: "changes", label: "Change history", component: ChangeHistory },
];

const ActivityLogTabs = () => {
  const [activeTab, setActiveTab] = useState("changes");
  const ActiveComponent = tabs.find((tab) => tab.key === activeTab)?.component;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-foreground">Activity Log</h1>

      <Tabs tabs={tabs} activeKey={activeTab} onChange={setActiveTab} />

      <div
        role="tabpanel"
        id={`tabpanel-${activeTab}`}
        aria-labelledby={`tab-${activeTab}`}
      >
        {ActiveComponent && <ActiveComponent />}
      </div>
    </div>
  );
};

export default ActivityLogTabs;
