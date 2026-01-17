import { authService } from "../services/auth";

const Navbar = () => {
  return (
    <nav className="w-full bg-secondary text-text-primary shadow-md">
      <div className="w-full px-6 py-4 flex items-center justify-between">
        {/* Left: Logo + App Name */}
        <div className="flex items-center gap-3">
          <img
            src="/src/assets/logo.png"
            alt="Caelum Logo"
            className="w-12 h-12 object-contain"
          />
          <span className="text-2xl font-bold tracking-wide">Caelum</span>
        </div>

        {/* Right: Logout */}
        <button
          onClick={() => authService.logout()}
          className="
            px-4 py-2 rounded-md
            bg-error
            text-text-primary
            font-medium
            hover:opacity-90
            focus:outline-none
            focus:ring-2 focus:ring-error
            transition border border-border
          "
        >
          Logout
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
