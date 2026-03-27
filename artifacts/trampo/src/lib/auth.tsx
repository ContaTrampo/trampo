import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { User, useGetMe } from "@workspace/api-client-react";
import { useQueryClient } from "@tanstack/react-query";

type AuthContextType = {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem("trampo_token"));
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem("trampo_user");
    return saved ? JSON.parse(saved) : null;
  });

  const queryClient = useQueryClient();

  const { data, isLoading, isError } = useGetMe({
    query: {
      enabled: !!token,
      retry: false,
    }
  });

  useEffect(() => {
    if (data) {
      setUser(data);
      localStorage.setItem("trampo_user", JSON.stringify(data));
    }
    if (isError) {
      setToken(null);
      setUser(null);
      localStorage.removeItem("trampo_token");
      localStorage.removeItem("trampo_user");
    }
  }, [data, isError]);

  const login = (newToken: string, newUser: User) => {
    setToken(newToken);
    setUser(newUser);
    localStorage.setItem("trampo_token", newToken);
    localStorage.setItem("trampo_user", JSON.stringify(newUser));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("trampo_token");
    localStorage.removeItem("trampo_user");
    queryClient.clear();
    window.location.href = import.meta.env.BASE_URL.replace(/\/$/, "") || "/";
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};
