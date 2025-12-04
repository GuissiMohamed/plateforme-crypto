import { useEffect, useState } from "react";
import { api, setAuthToken } from "../api";

export default function Profile({ onLogout }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    api.get("/users/me")
      .then(res => setUser(res.data))
      .catch(err => console.error("Erreur profil :", err));
  }, []);

  if (!user) return <p>Chargement…</p>;

  return (
    <div className="animate-fadeIn space-y-6">

      <div className="card">
        <h1 className="text-2xl font-semibold mb-2">Profil utilisateur</h1>
        <p className="text-text2 mb-4">Informations personnelles</p>

        <div className="space-y-2">
          <p>
            <span className="text-text2">Email : </span>
            <span className="font-semibold">{user.email}</span>
          </p>

          <p>
            <span className="text-text2">Utilisateur ID : </span>
            <span className="font-semibold">{user.id}</span>
          </p>

          <p>
            <span className="text-text2">Créé le : </span>
            <span className="font-semibold">
              {new Date(user.created_at).toLocaleString()}
            </span>
          </p>
        </div>
      </div>

      {/* CHANGER MOT DE PASSE (option visuelle) */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-3">Sécurité</h2>

        <button className="w-full btn-nav">
          🔐 Changer le mot de passe (visuel uniquement)
        </button>
      </div>

      {/* LOGOUT */}
      <button
        onClick={() => {
          setAuthToken(null);
          if (onLogout) onLogout();
        }}
        className="btn-logout w-full py-3 text-center"
      >
        🚪 Déconnexion
      </button>
    </div>
  );
}
