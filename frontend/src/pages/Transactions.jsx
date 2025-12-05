import { useEffect, useState } from "react";
import { api } from "../api";

export default function Transactions() {
  const [txs, setTxs] = useState([]);
  const [assets, setAssets] = useState({});
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const res = await api.get("/portfolio/transactions");
        const all = res.data;

        // Charger liste des assets pour avoir leur SYMBOL
        const assetsRes = await api.get("/assets?limit=200");
        const map = {};
        for (const a of assetsRes.data) {
          map[a.id] = a;
        }

        setAssets(map);
        setTxs(all);
      } catch (err) {
        console.error("Erreur transactions :", err);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  const filtered = txs
    .filter((t) =>
      filter === "all" ? true : filter === "buy" ? t.is_buy : !t.is_buy
    )
    .filter((t) =>
      t.asset_id.toLowerCase().includes(search.toLowerCase())
    );

  const formatDate = (d) =>
    new Date(d).toLocaleString("fr-FR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });

  if (loading) return <p>Chargement des transactions…</p>;

  return (
    <div className="animate-fadeIn space-y-6 p-6">
      <h1 className="text-3xl font-semibold">📜 Transactions</h1>

      {/* FILTRES */}
      <div className="flex gap-3">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="input-main"
          placeholder="Rechercher BTC / ETH…"
        />

        <select
          className="input-main"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="all">Toutes</option>
          <option value="buy">Achats</option>
          <option value="sell">Ventes</option>
        </select>
      </div>

      {/* TABLE */}
      <div className="card p-6 overflow-x-auto">
        {filtered.length === 0 ? (
          <p className="text-text2">Aucune transaction trouvée.</p>
        ) : (
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-dark3 text-text2">
                <th className="py-2">Type</th>
                <th className="py-2">Actif</th>
                <th className="py-2">Quantité</th>
                <th className="py-2">Prix ($)</th>
                <th className="py-2">Date</th>
              </tr>
            </thead>

            

            <tbody>
              {filtered.map((t) => {
                const a = assets[t.asset_id];
                const symbol = a ? a.symbol.toUpperCase() : t.asset_id;
                const type = t.is_buy ? "ACHAT" : "VENTE";
                const typeColor = t.is_buy ? "text-green-400" : "text-red-400";

                return (
                    
                  <tr key={t.id} className="border-b border-dark3">
                    <td className={`py-2 font-semibold ${typeColor}`}>
                      {type}
                    </td>
                    <td className="py-2">{symbol}</td>
                    <td className="py-2">{t.quantity}</td>
                    <td className="py-2">{t.price_usd.toFixed(2)} $</td>
                    <td className="py-2">{formatDate(t.timestamp)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
