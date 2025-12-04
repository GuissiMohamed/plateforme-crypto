export default function Sidebar({ onPageSelect, toggleTheme }) {
  return (
    <div className="w-64 bg-dark2 border-r border-dark3 flex flex-col p-4">
      
      {/* LOGO / TITLE */}
      <h2 className="text-2xl mb-6 font-semibold text-text">CryptoApp</h2>

      {/* MENU */}
      <button className="btn-nav" onClick={() => onPageSelect("dashboard")}>
        🏠 Dashboard
      </button>

      <button className="btn-nav" onClick={() => onPageSelect("market")}>
        📊 Marché
      </button>

      <button className="btn-nav" onClick={() => onPageSelect("portfolio")}>
        💼 Portefeuille
      </button>

      <button className="btn-nav" onClick={() => onPageSelect("profile")}>
        👤 Profil
      </button>

      {/* THEME SWITCH */}
      <button className="btn-nav" onClick={toggleTheme}>
        🌗 Mode
      </button>

      {/* LOGOUT */}
      <button 
        className="btn-logout mt-auto"
        onClick={() => onPageSelect("logout")}
      >
        🔓 Déconnexion
      </button>

    </div>
  );
}
