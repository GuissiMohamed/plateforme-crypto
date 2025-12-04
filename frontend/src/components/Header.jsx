// frontend/src/components/Header.jsx

import { useState, useEffect } from "react";
import { api } from "../api";

export default function Header({ title }) {
  const [notifications, setNotifications] = useState([]);
  const [showPanel, setShowPanel] = useState(false);

  // Charger notifications à l’ouverture
  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      const res = await api.get("/notifications");
      setNotifications(res.data);
    } catch (err) {
      console.error("Erreur chargement notifications :", err);
    }
  };

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  const markAsRead = async (notifId) => {
    try {
      await api.post(`/notifications/${notifId}/read`);
      setNotifications((prev) =>
        prev.map((n) =>
          n.id === notifId ? { ...n, is_read: true } : n
        )
      );
    } catch (err) {
      console.error("Erreur markAsRead :", err);
    }
  };

  return (
    <div className="flex justify-between items-center mb-6 relative">

      {/* 🔹 TITRE DE LA PAGE */}
      <h1 className="text-3xl font-semibold">{title}</h1>

      {/* 🔹 ZONE DROITE : NOTIFICATIONS */}
      <div className="relative">

        {/* Bouton Cloche */}
        <button
          onClick={() => setShowPanel(!showPanel)}
          className="relative text-2xl hover:opacity-80 transition"
        >
          🔔

          {/* Bulle rouge si notif non lue */}
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-2 bg-red-500 text-white text-xs px-1.5 py-0.5 rounded-full">
              {unreadCount}
            </span>
          )}
        </button>

        {/* PANNEAU DES NOTIFICATIONS */}
        {showPanel && (
          <div className="absolute right-0 mt-3 w-72 bg-dark2 border border-dark3 rounded-xl shadow-xl p-4 z-50">

            <h3 className="text-lg font-semibold mb-3">Notifications</h3>

            {notifications.length === 0 ? (
              <p className="text-text2 text-sm">Aucune notification.</p>
            ) : (
              notifications.map((n) => (
                <div
                  key={n.id}
                  className={`mb-3 p-3 rounded-lg text-sm ${
                    n.is_read ? "bg-dark3/50 text-text2" : "bg-dark3 text-white"
                  }`}
                >
                  <p>{n.message}</p>

                  {!n.is_read && (
                    <button
                      onClick={() => markAsRead(n.id)}
                      className="text-blue-400 text-xs mt-1 hover:underline"
                    >
                      Marquer comme lue
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
