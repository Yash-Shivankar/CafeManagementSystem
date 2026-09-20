import { Navigate, useLocation } from "react-router-dom";
import { usePermissions } from "../services/usePermissions";

const ProtectedRoute = ({ children, module }) => {
  const { isSignedIn, bootstrapped, canView } = usePermissions();
  const location = useLocation();

  if (!bootstrapped) return null;

  if (!isSignedIn) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (module && !canView(module)) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

export default ProtectedRoute;
