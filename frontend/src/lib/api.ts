const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface User {
  id: number;
  email: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PluginInfo {
  id: string;
  type: string;
  name: string;
  version: string;
  api_version: string;
  capabilities: string[];
  permissions: string[];
}

export interface AuditLog {
  id: number;
  user_id?: number;
  action: string;
  details?: Record<string, any>;
  created_at: string;
}

export interface DashboardStats {
  users_count: number;
  plugins_count: number;
  audit_logs_count: number;
  recent_logs: AuditLog[];
}

class ApiClient {
  private getToken(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem("orchx_token");
    }
    return null;
  }

  setToken(token: string) {
    if (typeof window !== "undefined") {
      localStorage.setItem("orchx_token", token);
    }
  }

  clearToken() {
    if (typeof window !== "undefined") {
      localStorage.removeItem("orchx_token");
    }
  }

  private getHeaders(isMultipart = false): HeadersInit {
    const headers: HeadersInit = {};
    if (!isMultipart) {
      headers["Content-Type"] = "application/json";
    }
    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  }

  async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const headers = {
      ...this.getHeaders(options.body instanceof FormData),
      ...options.headers,
    };

    const res = await fetch(`${BASE_URL}${path}`, {
      ...options,
      headers,
    });

    if (!res.ok) {
      let message = "An error occurred";
      try {
        const errData = await res.json();
        message = errData.detail || message;
      } catch (e) {}
      throw new Error(message);
    }

    return res.json() as Promise<T>;
  }

  async register(email: string, password: string): Promise<User> {
    return this.request<User>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  }

  async login(email: string, password: string): Promise<{ access_token: string }> {
    const formData = new FormData();
    formData.append("username", email);
    formData.append("password", password);

    const res = await this.request<{ access_token: string }>("/auth/login", {
      method: "POST",
      body: formData,
    });

    this.setToken(res.access_token);
    return res;
  }

  async getMe(): Promise<User> {
    return this.request<User>("/auth/me");
  }

  async getPlugins(): Promise<PluginInfo[]> {
    return this.request<PluginInfo[]>("/plugins/");
  }

  async getDashboardStats(): Promise<DashboardStats> {
    return this.request<DashboardStats>("/dashboard/stats");
  }
}

export const api = new ApiClient();
