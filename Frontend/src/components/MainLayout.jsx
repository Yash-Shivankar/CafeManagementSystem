import Navbar from "./Navbar";
import Sidebar from "./Sidebar";
import { Outlet } from "react-router-dom";

const MainLayout = () => {
  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Top Navbar */}
      <Navbar />

      {/* Sidebar + Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar now controls its own width */}
        <Sidebar />

        {/* Main content */}
        <main className="flex-1 overflow-y-auto p-4">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
