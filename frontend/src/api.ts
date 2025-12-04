import axios from "axios";

export const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// 🔐 Gestion du token JWT
export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    localStorage.setItem("token", token);
  } else {
    delete api.defaults.headers.common["Authorization"];
    localStorage.removeItem("token");
  }
}

// 🔄 Charger le token au démarrage
const saved = localStorage.getItem("token");
if (saved) setAuthToken(saved);

// ================================
// 💡 LOGIN CORRECT
// ================================
export async function loginRequest(email, password) {
  const form = new URLSearchParams();
  form.append("username", email);
  form.append("password", password);

  return api.post("/auth/login", form, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });
}
