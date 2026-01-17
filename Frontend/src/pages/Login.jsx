import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import ThemeSwitcher from "../components/ThemeSwitcher";
import { useLoginMutation } from "../app/allSlices";
import { authService } from "../services/auth";

const isEmail = (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);

const isMobile = (value) => /^[6-9]\d{9}$/.test(value);

const Login = () => {
  const navigate = useNavigate();
  const [login, { isLoading, isSuccess, error }] = useLoginMutation();

  const [form, setForm] = useState({
    username: "",
    password: "",
  });

  const [inputError, setInputError] = useState("");

  useEffect(() => {
    if (isSuccess) navigate("/");
  }, [isSuccess, navigate]);

  const handleUsernameChange = (value) => {
    setForm({ ...form, username: value });

    if (!value) {
      setInputError("");
      return;
    }

    if (!isEmail(value) && !isMobile(value)) {
      setInputError("Enter valid email or mobile number");
    } else {
      setInputError("");
    }
  };

  const submit = async (e) => {
    e.preventDefault();

    if (!form.username || !form.password) {
      setInputError("All fields are required");
      return;
    }

    if (!isEmail(form.username) && !isMobile(form.username)) {
      setInputError("Enter valid email or mobile number");
      return;
    }

    const payload = {
      password: form.password,
      ...(isEmail(form.username) && { email: form.username }),
      ...(isMobile(form.username) && { mobile_number: form.username }),
    };

    try {
      const response = await login(payload).unwrap();

      authService.setAuth(response);
      navigate("/");
    } catch (err) {
      console.error("Login failed:", err);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background text-text">
      <div
        className="
  w-full max-w-md p-8 rounded-2xl
  bg-[rgba(255,255,255,0.08)]
  backdrop-blur-xl
  border border-white/10
  shadow-[0_20px_50px_rgba(0,0,0,0.35)]
"
      >
        {/* <div className="flex justify-center mb-6">
          <h2 className="text-2xl font-bold">Login</h2>
        </div> */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-2">
            <span className="text-3xl">🔐</span>
            <h2 className="text-3xl font-extrabold tracking-wide">
              Welcome Back
            </h2>
          </div>
          <p className="text-sm text-text/70">
            Sign in to continue to your dashboard
          </p>
        </div>

        <form onSubmit={submit} className="space-y-4">
          <input
            className="w-full px-4 py-2 rounded bg-background border"
            placeholder="Email or Mobile Number"
            value={form.username}
            onChange={(e) => handleUsernameChange(e.target.value)}
          />

          {inputError && <p className="text-red-500 text-sm">{inputError}</p>}

          <input
            type="password"
            className="w-full px-4 py-2 rounded bg-background border"
            placeholder="Password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />

          {/* <button
            disabled={isLoading || inputError}
            className="w-full bg-primary text-white py-2 rounded disabled:opacity-50"
          >
            {isLoading ? "Logging in..." : "Login"}
          </button> */}
          <button
            type="submit"
            disabled={isLoading || inputError}
            className="
    w-full py-3 rounded-xl font-semibold
    bg-primary
    text-white
    relative z-10
    shadow-xl
    hover:brightness-110
    transition
    disabled:opacity-50 disabled:cursor-not-allowed
  "
          >
            {isLoading ? "Logging in..." : "Login"}
          </button>

          {error && (
            <p className="text-red-500 text-sm">
              {error?.data?.message || "Login failed"}
            </p>
          )}
        </form>

        <p className="text-sm text-center mt-4">
          No account?{" "}
          <Link to="/register" className="text-primary font-semibold">
            Register
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
