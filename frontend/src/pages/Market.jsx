import { useEffect, useState } from "react";
import { api } from "../api";

export default function Market({ onSelectAsset }) {
  const [assets, setAssets] = useState([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    api.get("/assets").then(res => setAssets(res.data));
  }, []);

  const filtered = assets.filter(a =>
    a.symbol.toLowerCase().includes(search.toLowerCase()) ||
    a.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="animate-slideLeft">
      <input
        placeholder="Rechercher BTC / Bitcoin…"
        className="input-main mb-5"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
        {filtered.map(a => (
          <div key={a.id} className="card" onClick={() => onSelectAsset(a.id)}>
            <h3 className="text-lg font-semibold">{a.symbol.toUpperCase()}</h3>
            <p className="text-text2">{a.name}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
