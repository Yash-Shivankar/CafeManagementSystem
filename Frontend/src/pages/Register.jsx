import { Link, useNavigate } from "react-router-dom";
import ThemeSwitcher from "../components/ThemeSwitcher";

const Register = () => {
  const navigate = useNavigate();

  const handleRegister = (e) => {
    e.preventDefault();
    navigate("/login");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background text-text">
      <div className="w-full max-w-md bg-secondary p-8 rounded-xl shadow-lg">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Register</h2>
          <ThemeSwitcher />
        </div>

        <form onSubmit={handleRegister} className="space-y-4">
          <input
            type="text"
            placeholder="Name"
            required
            className="w-full px-4 py-2 rounded bg-background text-text border"
          />

          <input
            type="email"
            placeholder="Email"
            required
            className="w-full px-4 py-2 rounded bg-background text-text border"
          />

          <input
            type="password"
            placeholder="Password"
            required
            className="w-full px-4 py-2 rounded bg-background text-text border"
          />

          <button className="w-full bg-primary text-white py-2 rounded font-semibold">
            Register
          </button>
        </form>

        <p className="text-sm mt-4 text-center">
          Already have an account?{" "}
          <Link to="/login" className="text-primary font-semibold">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
