import { useEffect, useState } from "react";
import { api } from "../api";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer
} from "recharts";

export default function Trade({ assetId, goBack }) {
  const [prices, setPrices] = useState([]);
  const [indicators, setIndicators] = useState(null);
  const [userHoldings, setUserHoldings] = useState(0);

  const [amount, setAmount] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    Promise.all([
      api.get(`/assets/${assetId}/prices?limit=40`),
      api.get(`/assets/${assetId}/indicators`),
      api.get("/portfolio/value"),
    ]).then(([p, ind, pf]) => {
      setPrices(
        p.data.map((d) => ({
          ...d,
          date: new Date(d.timestamp).toLocaleTimeString(),
        }))
      );
      setIndicators(ind.data);

      const found = pf.data.details?.find((item) => item.asset_id === assetId);
      setUserHoldings(found ? found.quantity : 0);
    });
  }, [assetId]);

  // ACHAT
  const handleBuy = async () => {
    if (!amount || amount <= 0) return;

    try {
      await api.post("/portfolio/buy", {
        asset_id: assetId,
        quantity: parseFloat(amount),
      });

      setMessage("Achat effectué ✔");
      setAmount("");

      const pf = await api.get("/portfolio/value");
      const found = pf.data.details?.find((i) => i.asset_id === assetId);
      setUserHoldings(found ? found.quantity : 0);

      setTimeout(() => setMessage(""), 3000);
    } catch {
      setMessage("Erreur lors de l'achat ❌");
      setTimeout(() => setMessage(""), 3000);
    }
  };

  // VENTE AVEC CHECK
  const handleSell = async () => {
    if (!amount || amount <= 0) return;

    if (parseFloat(amount) > userHoldings) {
      setMessage("❌ Quantité insuffisante pour vendre");
      return setTimeout(() => setMessage(""), 3000);
    }

    try {
      await api.post("/portfolio/sell", {
        asset_id: assetId,
        quantity: parseFloat(amount),
      });

      setMessage("Vente effectuée ✔");
      setAmount("");

      const pf = await api.get("/portfolio/value");
      const found = pf.data.details?.find((i) => i.asset_id === assetId);
      setUserHoldings(found ? found.quantity : 0);

      setTimeout(() => setMessage(""), 3000);
    } catch {
      setMessage("Erreur lors de la vente ❌");
      setTimeout(() => setMessage(""), 3000);
    }
  };

  return (
    <div className="animate-slideLeft space-y-6">
      
      <button onClick={goBack} className="btn-nav w-fit">
        ← Retour
      </button>

      {/* INFO CRYPTO */}
      {indicators && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-2">{assetId.toUpperCase()}</h2>

          <p className="mb-1">Prix actuel :
            <span className="text-primary"> {indicators.current_price?.toFixed(4)} $</span>
          </p>

          <p className="mb-1">Vos avoirs :
            <span className="text-accent"> {userHoldings} {assetId}</span>
          </p>
        </div>
      )}

      {/* GRAPHIQUE */}
      <div className="card h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={prices}>
            <XAxis dataKey="date" hide />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="price_usd" stroke="#58A6FF" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* TRADING */}
      <div className="card space-y-4">
        <h3 className="text-xl font-semibold">Trader {assetId.toUpperCase()}</h3>

        <input
          type="number"
          placeholder="Quantité"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          className="input-main"
        />

        <div className="flex gap-4">
          <button
            onClick={handleBuy}
            className="flex-1 bg-green-600 hover:bg-green-700 text-white py-3 rounded-lg transition shadow-soft"
          >
            Acheter
          </button>

          <button
            onClick={handleSell}
            className="flex-1 bg-red-600 hover:bg-red-700 text-white py-3 rounded-lg transition shadow-soft"
          >
            Vendre
          </button>
        </div>

        {message && (
          <p className="text-accent animate-pulseAccent">{message}</p>
        )}
      </div>
    </div>
  );
}
