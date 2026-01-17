import { Navigate } from "react-router-dom";
import { authService } from "../services/auth";

const ProtectedRoute = ({ children }) => {
  if (!authService.getToken()) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

export default ProtectedRoute;
