import { authService } from "../services/auth";

import logoWebp from "../assets/logo-512.webp";
import logoPng from "../assets/logo-512.png";
import OutletSwitcher from "./OutletSwitcher";

const Navbar = () => {
  return (
    <nav className="w-full bg-secondary text-on-secondary shadow-md">
      <div className="w-full px-6 py-4 flex items-center justify-between">

        <div className="flex items-center gap-3">
          <picture>
            <source srcSet={logoWebp} type="image/webp" />
            <img
              src={logoPng}
              alt="Caelum"
              width={48}
              height={48}
              className="w-12 h-12 object-contain"
            />
          </picture>
          <span className="text-2xl font-bold tracking-wide">Caelum</span>
        </div>

        <div className="flex items-center gap-4">
          <OutletSwitcher />

          <button
            onClick={() => authService.logout()}
            className="
              px-4 py-2 rounded-md
              bg-error
              text-on-error
              font-medium
              hover:opacity-90
              transition border border-border
            "
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
