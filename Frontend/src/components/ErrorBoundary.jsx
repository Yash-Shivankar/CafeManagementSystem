import { Component } from "react";
import Button from "./Button";
import { appUrl } from "../config/config";

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error("Unhandled UI error", error, info?.componentStack);
  }

  render() {
    const { error } = this.state;
    if (!error) return this.props.children;

    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-6">
        <div className="w-full max-w-md space-y-4 rounded-xl border border-border bg-surface p-8 text-center">
          <h1 className="text-xl font-semibold text-foreground">
            Something went wrong on this screen
          </h1>
          <p className="text-sm text-muted-foreground">
            Nothing you had already saved is affected. Reload to carry on, and
            tell us what you were doing if it keeps happening.
          </p>

          {import.meta.env.DEV && (
            <pre className="overflow-x-auto rounded-md bg-muted p-3 text-left text-xs text-muted-foreground">
              {String(error?.stack || error)}
            </pre>
          )}

          <div className="flex justify-center gap-2">
            <Button
              label="Reload"
              onClick={() => window.location.reload()}
            />
            <Button
              label="Back to dashboard"
              variant="outline"
              onClick={() => {
                window.location.href = appUrl("dashboard");
              }}
            />
          </div>
        </div>
      </div>
    );
  }
}

export default ErrorBoundary;
