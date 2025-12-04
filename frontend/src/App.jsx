import { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import Market from "./pages/Market";
import Details from "./pages/Details";
import Portfolio from "./pages/Portfolio";
import Trade from "./pages/Trade";
import Dashboard from "./pages/Dashboard";
import Profile from "./pages/Profile";
import { api, setAuthToken, loginRequest } from "./api";



export default function App() {
  const [theme, setTheme] = useState("dark");
  const [currentUser, setCurrentUser] = useState(null);

  // Gestion des pages : dashboard = page d’accueil
  const [page, setPage] = useState("dashboard");
  const [selectedAsset, setSelectedAsset] = useState(null);

  // Appliquer thème dark/light
  useEffect(() => {
    document.documentElement.className = theme;
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  // Vérification du token utilisateur
useEffect(() => {
  const handler = (e) => {
    const { asset, type } = e.detail;

    setSelectedAsset(asset);   // on sélectionne l'asset
    setPage("trade");          // on va à la page trade

    // transmettre le mode buy/sell si tu veux plus tard
    // localStorage.setItem("tradeMode", type);
  };

  window.addEventListener("go-trade", handler);
  return () => window.removeEventListener("go-trade", handler);
}, []);


  const handleLogout = () => {
    setAuthToken(null);
    setCurrentUser(null);
  };

  // Si pas encore connecté → page connexion
  if (!currentUser) return <Login onLogin={setCurrentUser} />;

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

        {/* HEADER AVEC TITRE DYNAMIQUE */}
        <Header title={
          page === "dashboard" ? "🏠 Dashboard" :
          page === "market" && !selectedAsset ? "📊 Marché" :
          page === "market" && selectedAsset ? `Détails — ${selectedAsset}` :
          page === "trade" ? `Trader — ${selectedAsset}` :
          page === "portfolio" ? "💼 Portefeuille" :
          page === "profile" ? "👤 Profil" :
          ""
        } />

        {/* ==== ROUTING INTERNE ==== */}

        {/* DASHBOARD */}
        {page === "dashboard" && <Dashboard />}

        {/* MARCHÉ */}
        {page === "market" && !selectedAsset && (
          <Market onSelectAsset={(id) => setSelectedAsset(id)} />
        )}

        {/* DETAILS → bouton Trader */}
        {page === "market" && selectedAsset && (
          <Details 
            assetId={selectedAsset}
            onTrade={() => setPage("trade")}
          />
        )}

        {/* PAGE TRADE */}
        {page === "trade" && selectedAsset && (
          <Trade 
            assetId={selectedAsset}
            goBack={() => setPage("market")}
          />
        )}

        {/* PORTFOLIO */}
        {page === "portfolio" && <Portfolio />}

        {/* PROFIL */}
        {page === "profile" && (
          <Profile onLogout={handleLogout} />
        )}

      </div>
    </div>
  );
}

///////////////////////////////////////////////////////////
// LOGIN PAGE
///////////////////////////////////////////////////////////

function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setErr("");

    try {
      const form = new URLSearchParams();
      form.append("username", email);
      form.append("password", password);

const res = await loginRequest(email, password);
      setAuthToken(res.data.access_token);

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
