import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import * as authApi from "@/lib/api";

// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext(undefined);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Restore the session from the httpOnly cookie on first load.
  useEffect(() => {
    // Tokens used to be kept here by the old Google sign-in; make sure none linger.
    try {
      localStorage.removeItem("birads_token");
    } catch {
      /* storage unavailable */
    }
    authApi.setSessionExpiredHandler(() => setUser(null));
    authApi
      .refreshSession()
      .then((res) => setUser(res.user))
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (email, password) => {
    const res = await authApi.login(email, password);
    setUser(res.user);
    return res.user;
  }, []);

  const changePassword = useCallback(async (currentPassword, newPassword) => {
    const res = await authApi.changePassword(currentPassword, newPassword);
    setUser(res.user);
  }, []);

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } finally {
      setUser(null);
    }
  }, []);

  const value = useMemo(
    () => ({ user, loading, login, changePassword, logout }),
    [user, loading, login, changePassword, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
