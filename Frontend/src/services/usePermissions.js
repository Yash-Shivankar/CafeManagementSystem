import { useSelector } from "react-redux";
import {
  selectBootstrapped,
  selectIsSignedIn,
  selectUser,
} from "../app/authSlice";
import {
  can,
  canCreate,
  canDelete,
  canUpdate,
  canView,
} from "../config/permissions";

export const usePermissions = () => {
  const user = useSelector(selectUser);
  const isSignedIn = useSelector(selectIsSignedIn);
  const bootstrapped = useSelector(selectBootstrapped);

  return {
    user,
    isSignedIn,
    bootstrapped,
    role: user?.role ?? null,
    can: (module, action) => can(user, module, action),
    canView: (module) => canView(user, module),
    canCreate: (module) => canCreate(user, module),
    canUpdate: (module) => canUpdate(user, module),
    canDelete: (module) => canDelete(user, module),
  };
};

export default usePermissions;
