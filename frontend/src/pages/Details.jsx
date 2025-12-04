import { useEffect, useState } from "react";
import { api } from "../api";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer
} from "recharts";

export default function Details({ assetId, onTrade }) {
  const [prices, setPrices] = useState([]);
  const [indicators, setIndicators] = useState(null);

  useEffect(() => {
    Promise.all([
      api.get(`/assets/${assetId}/prices?limit=50`),
      api.get(`/assets/${assetId}/indicators`)
    ])
    .then(([p, i]) => {
      setPrices(
        p.data.map((d) => ({
          ...d,
          date: new Date(d.timestamp).toLocaleTimeString(),
        }))
      );
      setIndicators(i.data);
    });
  }, [assetId]);

  return (
    <div className="animate-slideLeft space-y-6">

      {/* INDICATEURS */}
      {indicators && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-3">{assetId.toUpperCase()}</h2>

          <p className="mb-1">
            Prix actuel :
            <b className="text-primary"> {indicators.current_price?.toFixed(4)} $</b>
          </p>

          <p className="mb-1">
            Variation 24h :
            <span
              className={
                indicators.change_24h_pct >= 0
                  ? "text-green-400"
                  : "text-red-400"
              }
            >
              {" "}{indicators.change_24h_pct?.toFixed(2)}%
            </span>
          </p>

          <p className="mb-1">MA7 : {indicators.ma_short?.toFixed(4)}</p>
          <p className="mb-1">MA25 : {indicators.ma_long?.toFixed(4)}</p>

          <p className="mt-2">
            Signal :
            <b
              className={
                indicators.signal === "bullish"
                  ? "text-green-400"
                  : "text-red-400"
              }
            >
              {" "}{indicators.signal}
            </b>
          </p>
        </div>
      )}

      {/* GRAPHIQUE */}
      <div className="card h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={prices}>
            <XAxis dataKey="date" hide />
            <YAxis />
            <Tooltip />
            <Line 
              type="monotone" 
              dataKey="price_usd" 
              stroke="#58A6FF"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* BOUTON TRADER */}
      <button
        onClick={onTrade}
        className="w-full bg-accent text-black font-semibold py-3 rounded-lg mt-4
                   hover:shadow-glow-yellow transition-all duration-200 ease-soft"
      >
        🚀 Trader cette crypto
      </button>
    </div>
  );
}
