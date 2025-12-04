import { useEffect, useState } from "react";
import { api } from "../api";
import Sparkline from "../components/Sparkline";
import Skeleton from "../components/Skeleton";
import { PieChart, Pie, Tooltip, Cell, ResponsiveContainer } from "recharts";

export default function Dashboard() {
  const [portfolio, setPortfolio] = useState(null);
  const [historical, setHistorical] = useState({});
  const [loading, setLoading] = useState(true);

  const COLORS = ["#F0B90B", "#58A6FF", "#22c55e", "#f87171", "#d946ef", "#06b6d4"];

  useEffect(() => {
    async function load() {
      try {
        // 🔥 ROUTE CORRIGÉE
        const res = await api.get("/portfolio/value");
        const data = res.data;

        setPortfolio(data);

        const hist = {};
        for (const asset of data.details) {
          const r = await api.get(`/assets/${asset.asset_id}/prices?limit=40`);
          hist[asset.asset_id] = r.data.map((p) => p.price_usd || 0);
        }

        setHistorical(hist);
      } catch (e) {
        console.error("Erreur dashboard :", e);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  if (loading || !portfolio) {
    return (
      <div className="space-y-6 p-6 animate-fadeIn">
        <div className="card p-6 space-y-3">
          <Skeleton width="40%" height="24px" />
          <Skeleton width="30%" height="20px" />
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          <div className="card p-4"><Skeleton height="80px" /></div>
          <div className="card p-4"><Skeleton height="80px" /></div>
          <div className="card p-4"><Skeleton height="80px" /></div>
        </div>

        <div className="card p-6"><Skeleton height="260px" /></div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="card p-6"><Skeleton height="120px" /></div>
          <div className="card p-6"><Skeleton height="120px" /></div>
        </div>
      </div>
    );
  }

  const assets = portfolio.details.filter((a) => a.quantity > 0);
  const totalValue = portfolio.value_usd || 0;

  // Variation globale basée sur le premier asset
  let variation = 0;
  if (assets.length > 0) {
    const first = assets[0].asset_id;
    const hist = historical[first];
    if (hist && hist.length > 1) {
      const start = hist[0];
      const end = hist[hist.length - 1];
      variation = start !== 0 ? ((end - start) / start) * 100 : 0;
    }
  }

  const varClass = variation >= 0 ? "text-green-400" : "text-red-400";
  const safeFixed = (v) => (typeof v === "number" ? v.toFixed(2) : "0.00");

  const pieData = assets.map((a) => ({
    name: a.asset_id.toUpperCase(),
    value: Math.max(a.value_usd, totalValue * 0.02),
  }));

  const winLoss = assets.filter((a) => a.change_24h_pct != null);

  const winners = [...winLoss]
    .sort((a, b) => b.change_24h_pct - a.change_24h_pct)
    .slice(0, 3);

  const losers = [...winLoss]
    .sort((a, b) => a.change_24h_pct - b.change_24h_pct)
    .slice(0, 3);

  return (
    <div className="animate-fadeIn space-y-8 p-6">
      <div className="card flex justify-between items-center p-6">
        <div>
          <h1 className="text-3xl font-semibold">Dashboard</h1>
          <p className="text-text2">Vue d’ensemble de votre portefeuille</p>
        </div>

        <div className="text-right">
          <p className="text-2xl font-bold">{safeFixed(totalValue)} $</p>
          <p className={varClass}>
            {variation >= 0 ? "▲" : "▼"} {safeFixed(variation)}%
          </p>
        </div>
      </div>

      <div className="card p-6">
        <h2 className="text-xl font-semibold mb-4">Évolution globale</h2>

        <div className="grid md:grid-cols-3 gap-4">
          {assets.slice(0, 3).map((a) => (
            <div key={a.asset_id} className="p-3 rounded bg-dark2">
              <p className="font-semibold mb-2">
                {a.asset_id.toUpperCase()}
              </p>
              <Sparkline data={historical[a.asset_id]} />
            </div>
          ))}
        </div>
      </div>

      <div className="card p-6 h-80">
        <h2 className="text-xl font-semibold mb-4">Répartition du portefeuille</h2>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              outerRadius={110}
              dataKey="value"
              label={(entry) => entry.name}
            >
              {pieData.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="card p-6">
          <h2 className="text-xl font-semibold mb-4">Top Winners (24h)</h2>
          {winners.map((w) => (
            <div key={w.asset_id} className="flex justify-between p-2 border-b border-dark3">
              <span>{w.asset_id.toUpperCase()}</span>
              <span className="text-green-400">+{safeFixed(w.change_24h_pct)}%</span>
            </div>
          ))}
        </div>

        <div className="card p-6">
          <h2 className="text-xl font-semibold mb-4">Top Losers (24h)</h2>
          {losers.map((l) => (
            <div key={l.asset_id} className="flex justify-between p-2 border-b border-dark3">
              <span>{l.asset_id.toUpperCase()}</span>
              <span className="text-red-400">{safeFixed(l.change_24h_pct)}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
