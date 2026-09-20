import { Link } from "react-router-dom";

const NotFound = () => (
  <div className="flex min-h-[60vh] flex-col items-center justify-center gap-3 p-6 text-center">
    <p className="text-5xl font-bold text-primary">404</p>
    <h1 className="text-xl font-semibold text-foreground">
      That page does not exist
    </h1>
    <p className="max-w-sm text-sm text-muted-foreground">
      The link may be out of date, or you may not have access to this part of
      the app.
    </p>
    <Link
      to="/dashboard"
      className="mt-2 rounded-md bg-primary px-4 py-2 font-medium text-on-primary"
    >
      Back to dashboard
    </Link>
  </div>
);

export default NotFound;
