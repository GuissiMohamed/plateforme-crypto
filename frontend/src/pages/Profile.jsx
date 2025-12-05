// frontend/src/pages/Profile.jsx

import { useEffect, useState } from "react";
import { api, setAuthToken } from "../api";

export default function Profile({ onLogout }) {
  const [user, setUser] = useState(null);

  const [emailForm, setEmailForm] = useState({ new_email: "", password: "" });
  const [pwdForm, setPwdForm] = useState({ old_password: "", new_password: "" });
  const [profileForm, setProfileForm] = useState({ display_name: "", avatar_url: "" });
  const [webhookForm, setWebhookForm] = useState({ discord_webhook_url: "" });

  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const res = await api.get("/users/me");
        setUser(res.data);

        setProfileForm({
          display_name: res.data.display_name || "",
          avatar_url: res.data.avatar_url || "",
        });

        setWebhookForm({
          discord_webhook_url: res.data.discord_webhook_url || "",
        });

        setEmailForm((f) => ({ ...f, new_email: res.data.email }));
      } catch (e) {
        console.error("Erreur chargement profil :", e);
      }
    }

    load();
  }, []);

  const showMsg = (m) => {
    setMsg(m);
    setErr("");
  };
  const showErr = (e) => {
    setErr(e);
    setMsg("");
  };

  const handleEmailUpdate = async (e) => {
    e.preventDefault();
    try {
      await api.put("/users/me/email", emailForm);
      showMsg("Email mis à jour ✅");
    } catch (e) {
      console.error(e);
      showErr("Impossible de mettre à jour l'email.");
    }
  };

  const handlePwdUpdate = async (e) => {
    e.preventDefault();
    try {
      await api.put("/users/me/password", pwdForm);
      showMsg("Mot de passe mis à jour ✅");
      setPwdForm({ old_password: "", new_password: "" });
    } catch (e) {
      console.error(e);
      showErr("Ancien mot de passe invalide.");
    }
  };

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    try {
      await api.put("/users/me/profile", profileForm);
      showMsg("Profil mis à jour ✅");
    } catch (e) {
      console.error(e);
      showErr("Erreur lors de la mise à jour du profil.");
    }
  };

  const handleWebhookUpdate = async (e) => {
    e.preventDefault();
    try {
      await api.put("/users/me/discord-webhook", webhookForm);
      showMsg("Webhook Discord mis à jour ✅");
    } catch (e) {
      console.error(e);
      showErr("Erreur lors de la mise à jour du webhook.");
    }
  };

  const handleDeleteAccount = async () => {
    if (!window.confirm("⚠️ Es-tu sûr de vouloir supprimer ton compte ? Cette action est irréversible.")) {
      return;
    }

    try {
      await api.delete("/users/me");
      // on nettoie le token + logout
      setAuthToken(null);
      onLogout?.();
    } catch (e) {
      console.error(e);
      showErr("Erreur lors de la suppression du compte.");
    }
  };

  if (!user) {
    return <p>Chargement du profil…</p>;
  }

  return (
    <div className="animate-fadeIn space-y-6">

      <h1 className="text-3xl font-semibold mb-2">👤 Profil</h1>

      {msg && <p className="text-green-400">{msg}</p>}
      {err && <p className="text-red-400">{err}</p>}

      {/* Infos basiques */}
      <div className="card p-6 flex items-center gap-4">
        <div className="w-16 h-16 rounded-full bg-dark3 flex items-center justify-center text-2xl">
          {user.display_name
            ? user.display_name[0].toUpperCase()
            : user.email[0].toUpperCase()}
        </div>
        <div>
          <p className="font-semibold text-lg">
            {user.display_name || "Utilisateur"}
          </p>
          <p className="text-text2 text-sm">{user.email}</p>
        </div>
      </div>

      {/* Email */}
      <div className="card p-6 space-y-3">
        <h2 className="text-xl font-semibold">✉️ Changer d’email</h2>
        <form onSubmit={handleEmailUpdate} className="space-y-3 max-w-md">
          <input
            type="email"
            className="input-main"
            placeholder="Nouvel email"
            value={emailForm.new_email}
            onChange={(e) =>
              setEmailForm((f) => ({ ...f, new_email: e.target.value }))
            }
            required
          />
          <input
            type="password"
            className="input-main"
            placeholder="Mot de passe actuel"
            value={emailForm.password}
            onChange={(e) =>
              setEmailForm((f) => ({ ...f, password: e.target.value }))
            }
            required
          />
          <button className="btn-nav">Mettre à jour l’email</button>
        </form>
      </div>

      {/* Mot de passe */}
      <div className="card p-6 space-y-3">
        <h2 className="text-xl font-semibold">🔒 Changer le mot de passe</h2>
        <form onSubmit={handlePwdUpdate} className="space-y-3 max-w-md">
          <input
            type="password"
            className="input-main"
            placeholder="Ancien mot de passe"
            value={pwdForm.old_password}
            onChange={(e) =>
              setPwdForm((f) => ({ ...f, old_password: e.target.value }))
            }
            required
          />
          <input
            type="password"
            className="input-main"
            placeholder="Nouveau mot de passe"
            value={pwdForm.new_password}
            onChange={(e) =>
              setPwdForm((f) => ({ ...f, new_password: e.target.value }))
            }
            required
          />
          <button className="btn-nav">Mettre à jour le mot de passe</button>
        </form>
      </div>

      {/* Profil visuel */}
      <div className="card p-6 space-y-3">
        <h2 className="text-xl font-semibold">🧩 Infos de profil</h2>
        <form onSubmit={handleProfileUpdate} className="space-y-3 max-w-md">
          <input
            type="text"
            className="input-main"
            placeholder="Nom affiché"
            value={profileForm.display_name}
            onChange={(e) =>
              setProfileForm((f) => ({ ...f, display_name: e.target.value }))
            }
          />
          <input
            type="url"
            className="input-main"
            placeholder="URL de l’avatar (optionnel)"
            value={profileForm.avatar_url}
            onChange={(e) =>
              setProfileForm((f) => ({ ...f, avatar_url: e.target.value }))
            }
          />
          <button className="btn-nav">Mettre à jour le profil</button>
        </form>
      </div>

      {/* Webhook Discord */}
      <div className="card p-6 space-y-3">
        <h2 className="text-xl font-semibold">🔔 Webhook Discord</h2>
        <p className="text-text2 text-sm">
          Si tu mets un webhook Discord ici, tes alertes pourront être envoyées
          directement sur ton serveur (si ton alert_checker est configuré pour).
        </p>
        <form onSubmit={handleWebhookUpdate} className="space-y-3 max-w-xl">
          <input
            type="url"
            className="input-main"
            placeholder="https://discord.com/api/webhooks/… (vide pour supprimer)"
            value={webhookForm.discord_webhook_url}
            onChange={(e) =>
              setWebhookForm({ discord_webhook_url: e.target.value })
            }
          />
          <button className="btn-nav">Enregistrer le webhook</button>
        </form>
      </div>

      {/* Suppression compte */}
      <div className="card p-6 space-y-3 border border-red-500/40">
        <h2 className="text-xl font-semibold text-red-400">
          ⚠️ Zone de danger
        </h2>
        <p className="text-text2 text-sm">
          Supprimer ton compte effacera ton portefeuille, tes transactions, alertes et notifications.
          Cette action est irréversible.
        </p>
        <button className="btn-danger" onClick={handleDeleteAccount}>
          Supprimer définitivement mon compte
        </button>
      </div>
    </div>
  );
}
