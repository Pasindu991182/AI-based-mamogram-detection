import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import { fetchMe, loginWithGoogle, tokenStore } from "@/lib/api";

// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext(undefined);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Restore session from a stored token on first load.
  useEffect(() => {
    const token = tokenStore.get();
    if (!token) {
      setLoading(false);
      return;
    }
    fetchMe()
      .then(setUser)
      .catch(() => tokenStore.clear())
      .finally(() => setLoading(false));
  }, []);

  const loginWithGoogleCredential = useCallback(async (idToken) => {
    const res = await loginWithGoogle(idToken);
    tokenStore.set(res.access_token);
    setUser(res.user);
  }, []);

  const logout = useCallback(() => {
    tokenStore.clear();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, loading, loginWithGoogleCredential, logout }),
    [user, loading, loginWithGoogleCredential, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
