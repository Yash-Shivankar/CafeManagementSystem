const Dashboard = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-secondary p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-2">Welcome</h2>
          <p className="text-text-secondary">This is your dashboard overview</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
