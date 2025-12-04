import { useEffect, useState } from "react";
import { api } from "../api";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export default function Details({ assetId, onTrade }) {
  const [prices, setPrices] = useState([]);
  const [indicators, setIndicators] = useState(null);
  const [assetMeta, setAssetMeta] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!assetId) return;

    async function load() {
      setLoading(true);
      try {
        // 1) Historique des prix
        const [pricesRes, indRes, assetsRes] = await Promise.all([
          api.get(`/assets/${assetId}/prices?limit=100`),
          api.get(`/assets/${assetId}/indicators`),
          api.get("/assets?limit=200"),
        ]);

        const pricesData = pricesRes.data || [];
        setPrices(
          pricesData.map((p) => ({
            time: new Date(p.timestamp).toLocaleString(),
            price: p.price_usd,
          }))
        );

        setIndicators(indRes.data);

        const meta = (assetsRes.data || []).find((a) => a.id === assetId);
        setAssetMeta(meta || null);
      } catch (err) {
        console.error("Erreur chargement détails :", err);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [assetId]);

  if (loading || !indicators) {
    return (
      <div className="animate-fadeIn">
        <p>Chargement des détails…</p>
      </div>
    );
  }

  const name = assetMeta?.name || assetId.toUpperCase();
  const symbol = assetMeta?.symbol || assetId.slice(0, 4).toUpperCase();
  const currentPrice = indicators.current_price ?? 0;

  const safe = (v, digits = 2) =>
    typeof v === "number" ? v.toFixed(digits) : "—";

  const signalColor =
    indicators.signal === "bullish"
      ? "text-green-400"
      : indicators.signal === "bearish"
      ? "text-red-400"
      : "text-text2";

  return (
    <div className="animate-fadeIn space-y-6">

      {/* HEADER */}
      <div className="flex justify-between items-center card p-6">
        <div>
          <h1 className="text-3xl font-semibold">
            {name} <span className="text-text2 text-lg">({symbol})</span>
          </h1>
          <p className="text-text2">Analyse technique et historique de prix</p>
        </div>

        <div className="text-right">
          <p className="text-2xl font-bold">
            {safe(currentPrice, 4)} $
          </p>
          <p className={signalColor}>
            Signal : {indicators.signal || "—"}
          </p>
          <button
            className="btn-nav mt-3"
            onClick={onTrade}
          >
            Trader cette crypto
          </button>
        </div>
      </div>

      {/* GRAPHIQUE PRINCIPAL */}
      <div className="card p-6 h-80">
        <h2 className="text-xl font-semibold mb-4">Historique des prix</h2>
        {prices.length === 0 ? (
          <p className="text-text2">Pas encore de données de prix.</p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={prices}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
              <XAxis dataKey="time" hide />
              <YAxis domain={["auto", "auto"]} />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="price"
                stroke="#58A6FF"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* INDICATEURS TECHNIQUES */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">

        <IndicatorCard
          title="Moyennes mobiles (SMA)"
          items={[
            { label: "SMA courte", value: safe(indicators.ma_short) },
            { label: "SMA longue", value: safe(indicators.ma_long) },
          ]}
        />

        <IndicatorCard
          title="Moyennes mobiles (EMA)"
          items={[
            { label: "EMA 12", value: safe(indicators.ema_short) },
            { label: "EMA 26", value: safe(indicators.ema_long) },
          ]}
        />

        <IndicatorCard
          title="RSI (14 périodes)"
          items={[
            {
              label: "RSI",
              value: safe(indicators.rsi),
            },
            {
              label: "Zone",
              value:
                indicators.rsi == null
                  ? "—"
                  : indicators.rsi > 70
                  ? "Surachat"
                  : indicators.rsi < 30
                  ? "Survente"
                  : "Neutre",
            },
          ]}
        />

        <IndicatorCard
          title="MACD (12/26/9)"
          items={[
            { label: "MACD", value: safe(indicators.macd, 4) },
            { label: "Signal", value: safe(indicators.macd_signal, 4) },
            { label: "Histogramme", value: safe(indicators.macd_hist, 4) },
          ]}
        />

        <IndicatorCard
          title="Variation 24h"
          items={[
            {
              label: "Δ 24h",
              value:
                indicators.change_24h_pct != null
                  ? `${safe(indicators.change_24h_pct)} %`
                  : "—",
            },
          ]}
        />

        <IndicatorCard
          title="Résumé"
          items={[
            { label: "Signal global", value: indicators.signal || "—" },
            {
              label: "Tendance",
              value:
                indicators.ma_short != null &&
                indicators.ma_long != null &&
                indicators.ma_short > indicators.ma_long
                  ? "Tendance haussière"
                  : "Tendance baissière ou neutre",
            },
          ]}
        />
      </div>
    </div>
  );
}

function IndicatorCard({ title, items }) {
  return (
    <div className="card p-5 space-y-2">
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      {items.map((it, idx) => (
        <div key={idx} className="flex justify-between text-sm">
          <span className="text-text2">{it.label}</span>
          <span className="font-semibold">{it.value}</span>
        </div>
      ))}
    </div>
  );
}
