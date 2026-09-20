import { useEffect, useState } from "react";
import { useLocation, useNavigate, Link } from "react-router-dom";
import { useLoginMutation } from "../app/allSlices";
import { authService } from "../services/auth";
import Button from "../components/Button";

import logoWebp from "../assets/logo-512.webp";
import logoPng from "../assets/logo-512.png";

const isEmail = (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
const isMobile = (value) => /^[6-9]\d{9}$/.test(value);

const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [login, { isLoading, isSuccess, error }] = useLoginMutation();

  const destination = location.state?.from?.pathname || "/";

  const [form, setForm] = useState({ username: "", password: "" });
  const [inputError, setInputError] = useState("");

  useEffect(() => {
    if (isSuccess) navigate(destination, { replace: true });
  }, [isSuccess, navigate, destination]);

  const handleUsernameChange = (value) => {
    setForm((prev) => ({ ...prev, username: value }));

    if (!value) {
      setInputError("");
    } else if (!isEmail(value) && !isMobile(value)) {
      setInputError("Enter a valid email address or 10-digit mobile number");
    } else {
      setInputError("");
    }
  };

  const submit = async (e) => {
    e.preventDefault();

    if (!form.username || !form.password) {
      setInputError("Enter your email or mobile number and your password");
      return;
    }

    if (!isEmail(form.username) && !isMobile(form.username)) {
      setInputError("Enter a valid email address or 10-digit mobile number");
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
      navigate(destination, { replace: true });
    } catch {
    }
  };

  const inputClass =
    "w-full rounded-md border border-border bg-background px-4 py-2 " +
    "text-foreground placeholder:text-muted-foreground";

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-md rounded-xl border border-border bg-surface p-8 shadow-lg">
        <div className="mb-8 text-center">
          <picture>
            <source srcSet={logoWebp} type="image/webp" />
            <img
              src={logoPng}
              alt=""
              width={48}
              height={48}
              className="mx-auto mb-4 h-12 w-12 object-contain"
            />
          </picture>
          <h1 className="text-2xl font-bold text-foreground">Welcome back</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Sign in to continue to your dashboard
          </p>
        </div>

        <form onSubmit={submit} className="space-y-4" noValidate>
          <div className="space-y-1">
            <label
              htmlFor="login-username"
              className="block text-sm font-medium text-foreground"
            >
              Email or mobile number
            </label>
            <input
              id="login-username"
              name="username"
              autoComplete="username"
              autoFocus
              aria-invalid={inputError ? true : undefined}
              aria-describedby={inputError ? "login-error" : undefined}
              className={inputClass}
              placeholder="you@cafe.com or 9876543210"
              value={form.username}
              onChange={(e) => handleUsernameChange(e.target.value)}
            />
          </div>

          <div className="space-y-1">
            <label
              htmlFor="login-password"
              className="block text-sm font-medium text-foreground"
            >
              Password
            </label>
            <input
              id="login-password"
              name="password"
              type="password"
              autoComplete="current-password"
              className={inputClass}
              value={form.password}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, password: e.target.value }))
              }
            />
          </div>

          <div id="login-error" role="alert" aria-live="polite">
            {(inputError || error) && (
              <p className="text-sm text-error">
                {inputError ||
                  error?.data?.detail ||
                  "Sign-in failed. Check your details and try again."}
              </p>
            )}
          </div>

          <Button
            type="submit"
            label={isLoading ? "Signing in…" : "Sign in"}
            loading={isLoading}
            disabled={Boolean(inputError)}
            className="w-full"
            size="lg"
          />
        </form>

        <p className="mt-6 text-center text-sm text-muted-foreground">
          No account?{" "}
          <Link to="/register" className="font-semibold text-primary">
            Register
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
