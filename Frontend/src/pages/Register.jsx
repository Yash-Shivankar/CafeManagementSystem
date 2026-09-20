import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import ThemeSwitcher from "../components/ThemeSwitcher";
import { useRegisterMutation } from "../app/allSlices";
import { authService } from "../services/auth";

const isEmail = (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
const isMobile = (value) => /^[6-9]\d{9}$/.test(value);

const Register = () => {
  const navigate = useNavigate();
  const [register, { isLoading }] = useRegisterMutation();

  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    username: "",
    password: "",
  });
  const [inputError, setInputError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setInputError("");

    if (!form.username || !form.password) {
      setInputError("All fields are required");
      return;
    }

    if (!isEmail(form.username) && !isMobile(form.username)) {
      setInputError("Enter a valid email or mobile number");
      return;
    }

    if (form.password.length < 8) {
      setInputError("Password must be at least 8 characters");
      return;
    }

    const payload = {
      first_name: form.first_name || null,
      last_name: form.last_name || null,
      password: form.password,
      ...(isEmail(form.username) && { email: form.username }),
      ...(isMobile(form.username) && { mobile_number: form.username }),
    };

    try {
      const response = await register(payload).unwrap();
      authService.setAuth(response);
      toast.success("Welcome to Caelum");
      navigate("/");
    } catch (err) {
      setInputError(err?.data?.detail || "Registration failed");
    }
  };

  const field = (key) => ({
    value: form[key],
    onChange: (e) => setForm({ ...form, [key]: e.target.value }),
  });

  return (
    <div className="min-h-screen flex items-center justify-center bg-background text-text">
      <div className="w-full max-w-md bg-secondary p-8 rounded-xl shadow-lg">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Register</h2>
          <ThemeSwitcher />
        </div>

        <form onSubmit={submit} className="space-y-4">
          <input
            type="text"
            placeholder="First name"
            className="w-full px-4 py-2 rounded bg-background text-text border"
            {...field("first_name")}
          />

          <input
            type="text"
            placeholder="Last name"
            className="w-full px-4 py-2 rounded bg-background text-text border"
            {...field("last_name")}
          />

          <input
            type="text"
            placeholder="Email or mobile number"
            required
            className="w-full px-4 py-2 rounded bg-background text-text border"
            {...field("username")}
          />

          <input
            type="password"
            placeholder="Password (min 8 characters)"
            required
            className="w-full px-4 py-2 rounded bg-background text-text border"
            {...field("password")}
          />

          {inputError && <p className="text-red-500 text-sm">{inputError}</p>}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-primary text-white py-2 rounded font-semibold disabled:opacity-50"
          >
            {isLoading ? "Creating account..." : "Register"}
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
