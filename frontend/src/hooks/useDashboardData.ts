import { useState, useEffect } from "react";
import { api, DashboardStats, PluginInfo } from "@/lib/api";

export function useDashboardData(token: string | null) {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [plugins, setPlugins] = useState<PluginInfo[]>([]);
  const [loading, setLoading] = useState(true);

  const loadDashboardData = async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const [statsData, pluginsData] = await Promise.all([
        api.getDashboardStats(),
        api.getPlugins(),
      ]);
      setStats(statsData);
      setPlugins(pluginsData);
    } catch (err) {
      console.error("Failed to load kernel stats", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      loadDashboardData();
      
      // Polling isolated here. Will reconnect fully in Phase 4 when Runtime Observatory is built.
      const interval = setInterval(() => {
        // loadDashboardData(true);
      }, 5000);
      
      return () => clearInterval(interval);
    }
  }, [token]);

  return { stats, plugins, loading, loadDashboardData };
}
