import { useState, useEffect } from "react";
import { api, User } from "@/lib/api";

export function useAuth() {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const savedToken = localStorage.getItem("orchx_token");
    if (savedToken) {
      setToken(savedToken);
      fetchUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUser = async () => {
    try {
      const u = await api.getMe();
      setUser(u);
    } catch (err) {
      handleLogout();
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    api.clearToken();
    setToken(null);
    setUser(null);
  };

  return { token, setToken, user, fetchUser, handleLogout, loading };
}
