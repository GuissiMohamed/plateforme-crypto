import { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import Market from "./pages/Market";
import Details from "./pages/Details";
import Portfolio from "./pages/Portfolio";
import Trade from "./pages/Trade";
import Dashboard from "./pages/Dashboard";
import Profile from "./pages/Profile";
import Transactions from "./pages/Transactions";
import { api, setAuthToken, loginRequest } from "./api";

export default function App() {
  const [theme, setTheme] = useState("dark");
  const [currentUser, setCurrentUser] = useState(null);

  const [page, setPage] = useState("dashboard");
  const [selectedAsset, setSelectedAsset] = useState(null);

  // 🎨 Gestion du thème
  useEffect(() => {
    document.documentElement.className = theme;
  }, [theme]);

  const toggleTheme = () => {
    setTheme((t) => (t === "dark" ? "light" : "dark"));
  };

  // 🔁 Récupérer token + user au chargement
  useEffect(() => {
    const token = localStorage.getItem("token");

    if (token) {
      setAuthToken(token);

      api
        .get("/users/me")
        .then((res) => setCurrentUser(res.data))
        .catch(() => {
          setAuthToken(null);
          setCurrentUser(null);
        });
    }
  }, []);

  // 🎯 Écouteur global pour ouvrir Trade depuis Market ou Portfolio
  useEffect(() => {
    const handler = (e) => {
      const { asset } = e.detail;
      setSelectedAsset(asset);
      setPage("trade");
    };

    window.addEventListener("go-trade", handler);
    return () => window.removeEventListener("go-trade", handler);
  }, []);

  const handleLogout = () => {
    setAuthToken(null);
    setCurrentUser(null);
  };

  // 🟦--------------- LOGIN PAGE --------------------
  if (!currentUser) return <Login onLogin={setCurrentUser} />;

  // 🟩--------------- APP VISITEUR ------------------
  return (
    <div className="flex h-screen bg-dark text-text">

      {/* SIDEBAR */}
      <Sidebar
        onPageSelect={(p) => {
          if (p === "logout") return handleLogout();
          setPage(p);
          setSelectedAsset(null);
        }}
        toggleTheme={toggleTheme}
      />

      {/* ZONE PRINCIPALE */}
      <div className="flex-1 p-6 overflow-y-auto">
        <Header
          title={
            page === "dashboard" ? "🏠 Dashboard" :
            page === "market" && !selectedAsset ? "📊 Marché" :
            page === "market" && selectedAsset ? `Détails — ${selectedAsset}` :
            page === "trade" ? `Trader — ${selectedAsset}` :
            page === "portfolio" ? "💼 Portefeuille" :
            page === "profile" ? "👤 Profil" : ""
            
          }
        />

        {/* ROUTES INTERNES */}
        {page === "dashboard" && <Dashboard />}
        {page === "market" && !selectedAsset && (
          <Market onSelectAsset={(id) => setSelectedAsset(id)} />
        )}
        {page === "market" && selectedAsset && (
          <Details assetId={selectedAsset} onTrade={() => setPage("trade")} />
        )}
        {page === "trade" && selectedAsset && (
          <Trade assetId={selectedAsset} goBack={() => setPage("market")} />
        )}
        {page === "portfolio" && <Portfolio />}
        {page === "profile" && <Profile onLogout={handleLogout} />}
        {page === "transactions" && <Transactions />}

      </div>
    </div>
  );
}

// =======================================================
// 🔐 PAGE LOGIN
// =======================================================

function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setErr("");

    try {
      const res = await loginRequest(email, password);
      const token = res.data.access_token;

      setAuthToken(token);

      const me = await api.get("/users/me");
      onLogin(me.data);
    } catch {
      setErr("Email ou mot de passe incorrect.");
    }
  };

  return (
    <div className="flex items-center justify-center h-screen bg-dark">
      <form
        onSubmit={handleLogin}
        className="bg-dark2 p-6 rounded-xl border border-dark3 shadow-soft w-80"
      >
        <h2 className="text-2xl mb-4 font-semibold">Connexion</h2>

        <input
          type="email"
          placeholder="Email"
          className="input-main mb-3"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <input
          type="password"
          placeholder="Mot de passe"
          className="input-main mb-4"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button className="btn-nav w-full">Se connecter</button>

        {err && <p className="text-red-400 mt-2">{err}</p>}
      </form>
    </div>
  );
}
