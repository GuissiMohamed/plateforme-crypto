import { useEffect, useState } from "react";
import { api } from "../api";
import Sparkline from "../components/Sparkline";
import Skeleton from "../components/Skeleton";

export default function Portfolio() {
  const [portfolio, setPortfolio] = useState(null);
  const [historical, setHistorical] = useState({});
  const [loading, setLoading] = useState(true);

  const refresh = async () => {
    setLoading(true);
    try {
      // 🔥 ROUTE CORRIGÉE
      const res = await api.get("/portfolio/value");

      const hist = {};
      for (const a of res.data.details) {
        const r = await api.get(`/assets/${a.asset_id}/prices?limit=30`);
        hist[a.asset_id] = r.data.map((p) => p.price_usd || 0);
      }

      setHistorical(hist);
      setPortfolio(res.data);
    } catch (err) {
      console.error("Erreur portefeuille :", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const safeFixed = (v) => (typeof v === "number" ? v.toFixed(2) : "0.00");

  if (loading || !portfolio) {
    return (
      <div className="space-y-6 animate-fadeIn">
        <Skeleton width="40%" height="28px" />
        <div className="card p-6 space-y-3">
          <Skeleton height="20px" />
          <Skeleton height="20px" />
          <Skeleton height="20px" />
        </div>
      </div>
    );
  }

  const assets = portfolio.details.filter((p) => p.quantity > 0);

  return (
    <div className="animate-fadeIn space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-semibold">💼 Portefeuille</h1>
        <button onClick={refresh} className="btn-nav">🔄 Actualiser</button>
      </div>

      <div className="card p-6">
        <h2 className="text-xl font-semibold mb-2">Valeur totale</h2>
        <p className="text-3xl font-bold">{safeFixed(portfolio.value_usd)} $</p>
      </div>

      <div className="card p-6">
        <h2 className="text-xl font-semibold mb-4">Vos positions</h2>

        {assets.length === 0 ? (
          <p className="text-text2">Aucune position pour le moment.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-dark3 text-text2">
                  <th className="py-2">Actif</th>
                  <th className="py-2">Quantité</th>
                  <th className="py-2">Valeur ($)</th>
                  <th className="py-2">Variation (24h)</th>
                  <th className="py-2">Graphique</th>
                  <th className="py-2 text-right">Actions</th>
                </tr>
              </thead>

              <tbody>
                {assets.map((a) => {
                  const change = a.change_24h_pct || 0;
                  const isUp = change >= 0;

                  return (
                    <tr key={a.asset_id} className="border-b border-dark3">
                      <td className="py-3 font-semibold">
                        {a.asset_id.toUpperCase()}
                      </td>
                      <td className="py-3">{a.quantity}</td>
                      <td className="py-3">{safeFixed(a.value_usd)} $</td>

                      <td className={`py-3 font-semibold ${isUp ? "text-green-400" : "text-red-400"}`}>
                        {isUp ? "▲" : "▼"} {safeFixed(change)}%
                      </td>

                      <td className="py-3 w-40">
                        <Sparkline data={historical[a.asset_id]} />
                      </td>

                      <td className="py-3 text-right">
                        <button
                          className="btn-nav mr-2"
                          onClick={() =>
                            window.dispatchEvent(
                              new CustomEvent("go-trade", {
                                detail: { asset: a.asset_id, type: "buy" },
                              })
                            )
                          }
                        >
                          Acheter
                        </button>

                        <button
                          className="btn-danger"
                          onClick={() =>
                            window.dispatchEvent(
                              new CustomEvent("go-trade", {
                                detail: { asset: a.asset_id, type: "sell" },
                              })
                            )
                          }
                        >
                          Vendre
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
