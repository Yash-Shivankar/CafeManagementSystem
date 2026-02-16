import { useState } from "react";
import Users from "./Users";
import Roles from "./Roles";

const UsersTabs = () => {
  const [tab, setTab] = useState("users");

  return (
    <div className="p-4 space-y-6">
      {/* Tabs */}
      <div className="flex gap-4 border-b">
        <button
          className={`pb-2 ${
            tab === "users" ? "border-b-2 border-blue-500 font-bold" : ""
          }`}
          onClick={() => setTab("users")}
        >
          Users
        </button>

        <button
          className={`pb-2 ${
            tab === "roles" ? "border-b-2 border-blue-500 font-bold" : ""
          }`}
          onClick={() => setTab("roles")}
        >
          Roles
        </button>
      </div>

      {/* Tab Content */}
      <div>{tab === "users" ? <Users /> : <Roles />}</div>
    </div>
  );
};

export default UsersTabs;
