import { useEffect, useState } from "react";
import { api, setAuthToken } from "./api";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

// ------------------ STYLES REUTILISABLES ------------------ //
const inputStyle = {
  width: "100%",
  padding: "10px",
  borderRadius: "8px",
  background: "#0b1120",
  border: "1px solid #1e293b",
  color: "white",
  marginBottom: "10px",
};

const button = {
  padding: "10px",
  borderRadius: "8px",
  border: "none",
  cursor: "pointer",
};

const buttonPrimary = {
  ...button,
  background: "#3b82f6",
  width: "100%",
  color: "white",
  marginTop: "10px",
};

const card = {
  background: "#1e293b",
  padding: "15px",
  borderRadius: "10px",
  marginBottom: "15px",
};

const sidebar = {
  width: "230px",
  background: "#1e293b",
  padding: "20px",
  display: "flex",
  flexDirection: "column",
  gap: "10px",
};

const navBtn = {
  ...button,
  background: "#334155",
  color: "white",
  marginBottom: "5px",
};

const logoutBtn = {
  ...button,
  background: "#ef4444",
  color: "white",
  marginTop: "20px",
};


// ------------------ APP MAIN ------------------ //

export default function App() {
  // AUTH
  const [currentUser, setCurrentUser] = useState(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authError, setAuthError] = useState("");

  // MARKET
  const [assets, setAssets] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [search, setSearch] = useState("");

  // DETAILS
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [prices, setPrices] = useState([]);
  const [indicators, setIndicators] = useState(null);

  // PORTFOLIO
  const [portfolio, setPortfolio] = useState(null);
  const [buyQty, setBuyQty] = useState("");
  const [sellQty, setSellQty] = useState("");


  // -------------- LOGIN ------------------ //
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;

    api
      .get("/users/me")
      .then((res) => setCurrentUser(res.data))
      .catch(() => setAuthToken(null));
  }, []);

  const login = async (e) => {
    e.preventDefault();
    setAuthError("");

    try {
      const form = new URLSearchParams();
      form.append("username", email);
      form.append("password", password);

      const res = await api.post("/auth/login", form);
      const token = res.data.access_token;

      setAuthToken(token);
      const me = await api.get("/users/me");
      setCurrentUser(me.data);
    } catch {
      setAuthError("Identifiants incorrects.");
    }
  };

  const logout = () => {
    setAuthToken(null);
    setCurrentUser(null);
  };


  // -------------- ASSETS LIST ------------------ //
  useEffect(() => {
    api.get("/assets?limit=50").then((res) => {
      setAssets(res.data);
      setFiltered(res.data);
    });
  }, []);

  useEffect(() => {
    const q = search.toLowerCase();
    setFiltered(
      assets.filter(
        (a) =>
          a.symbol.toLowerCase().includes(q) ||
          a.name.toLowerCase().includes(q)
      )
    );
  }, [search, assets]);


  // -------------- DETAILS ------------------ //
  const loadDetails = (id) => {
    setSelectedAsset(id);

    Promise.all([
      api.get(`/assets/${id}/prices?limit=50`),
      api.get(`/assets/${id}/indicators`),
    ]).then(([p, i]) => {
      setPrices(
        p.data.map((d) => ({
          ...d,
          date: new Date(d.timestamp).toLocaleTimeString(),
        }))
      );
      setIndicators(i.data);
    });
  };


  // -------------- PORTFOLIO ------------------ //
  const refreshPortfolio = () => {
    if (!currentUser) return;
    api.get("/portfolio/value").then((res) => setPortfolio(res.data));
  };

  useEffect(() => {
    refreshPortfolio();
  }, [currentUser]);


  const buy = async () => {
    if (!selectedAsset) return;
    await api.post("/portfolio/buy", {
      asset_id: selectedAsset,
      quantity: Number(buyQty),
    });
    setBuyQty("");
    refreshPortfolio();
  };

  const sell = async () => {
    if (!selectedAsset) return;
    await api.post("/portfolio/sell", {
      asset_id: selectedAsset,
      quantity: Number(sellQty),
    });
    setSellQty("");
    refreshPortfolio();
  };


  // -------------- LOGIN PAGE ------------------ //
  if (!currentUser) {
    return (
      <div style={{ display: "flex", height: "100vh" }}>
        <form
          onSubmit={login}
          style={{
            margin: "auto",
            background: "#1e293b",
            padding: 30,
            borderRadius: 12,
            width: 350,
          }}
        >
          <h2 style={{ marginBottom: 20 }}>Connexion</h2>

          <input
            type="email"
            placeholder="Email"
            value={email}
            required
            onChange={(e) => setEmail(e.target.value)}
            style={inputStyle}
          />

          <input
            type="password"
            placeholder="Mot de passe"
            value={password}
            required
            onChange={(e) => setPassword(e.target.value)}
            style={inputStyle}
          />

          <button style={buttonPrimary}>Se connecter</button>

          {authError && <p style={{ color: "tomato" }}>{authError}</p>}
        </form>
      </div>
    );
  }



  // -------------- MAIN APP ------------------ //
  return (
    <div style={{ display: "flex", height: "100vh", overflow: "hidden" }}>
      {/* SIDEBAR */}
      <div style={sidebar}>
        <h2>CryptoApp</h2>
        <button onClick={() => setSelectedAsset(null)} style={navBtn}>
          📊 Marché
        </button>
        <button onClick={refreshPortfolio} style={navBtn}>
          💼 Portefeuille
        </button>
        <button onClick={logout} style={logoutBtn}>
          🔓 Déconnexion
        </button>
      </div>

      {/* CONTENT */}
      <div style={{ flex: 1, padding: 20, overflowY: "auto" }}>
        {/* MARKET PAGE */}
        {!selectedAsset ? (
          <>
            <h1>📊 Marché</h1>

            <input
              placeholder="Rechercher BTC / Bitcoin..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ ...inputStyle, marginBottom: 20 }}
            />

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
                gap: 15,
              }}
            >
              {filtered.map((a) => (
                <div key={a.id} onClick={() => loadDetails(a.id)} style={card}>
                  <h3>{a.symbol.toUpperCase()}</h3>
                  <p>{a.name}</p>
                </div>
              ))}
            </div>

            <h2 style={{ marginTop: 30 }}>💼 Portefeuille</h2>
            {portfolio ? (
              <div style={card}>
                <p>Valeur totale : {portfolio.value_usd.toFixed(2)} $</p>

                {portfolio.details.length > 0 ? (
                  portfolio.details.map((p) => (
                    <p key={p.asset_id}>
                      {p.asset_id} : {p.quantity} →{" "}
                      {p.value_usd.toFixed(2)} $
                    </p>
                  ))
                ) : (
                  <p>Aucune position.</p>
                )}
              </div>
            ) : (
              <p>Chargement…</p>
            )}
          </>
        ) : (
          <>
            {/* DETAILS PAGE */}
            <button onClick={() => setSelectedAsset(null)} style={navBtn}>
              ⬅ Retour
            </button>

            <h1>📈 {selectedAsset}</h1>

            {indicators && (
              <div style={card}>
                <p>Prix actuel : {indicators.current_price?.toFixed(4)} $</p>
                <p>Variation 24h : {indicators.change_24h_pct?.toFixed(2)}%</p>
                <p>MA courte : {indicators.ma_short?.toFixed(4)}</p>
                <p>MA longue : {indicators.ma_long?.toFixed(4)}</p>
                <p>
                  Signal :{" "}
                  <b
                    style={{
                      color:
                        indicators.signal === "bullish"
                          ? "lime"
                          : indicators.signal === "bearish"
                          ? "tomato"
                          : "white",
                    }}
                  >
                    {indicators.signal}
                  </b>
                </p>
              </div>
            )}

            {/* GRAPH */}
            <div style={{ height: 300, marginTop: 20, ...card }}>
              {prices.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={prices}>
                    <XAxis dataKey="date" hide />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="price_usd"
                      stroke="#3b82f6"
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <p>Aucune donnée</p>
              )}
            </div>

            {/* BUY / SELL */}
            <div style={card}>
              <h3>Trader</h3>

              <div>
                <input
                  type="number"
                  placeholder="Acheter quantité"
                  value={buyQty}
                  onChange={(e) => setBuyQty(e.target.value)}
                  style={inputStyle}
                />
                <button onClick={buy} style={buttonPrimary}>
                  Acheter
                </button>
              </div>

              <div style={{ marginTop: 10 }}>
                <input
                  type="number"
                  placeholder="Vendre quantité"
                  value={sellQty}
                  onChange={(e) => setSellQty(e.target.value)}
                  style={inputStyle}
                />
                <button
                  onClick={sell}
                  style={{ ...buttonPrimary, background: "#f97316" }}
                >
                  Vendre
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
